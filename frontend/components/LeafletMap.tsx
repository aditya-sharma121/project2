"use client";

import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface IncidentFeature {
  id: string;
  lat: number;
  lng: number;
  title: string;
  severity: string;
  confidence: number;
  status: string;
  isSimulated: boolean;
  freshnessMin?: number;
}

interface RoadFeature {
  id: string;
  name: string;
  coordinates: [number, number][]; // [ [lng, lat], ... ]
  riskScore: number;
  riskLevel: string;
  isBlocked: boolean;
}

interface FacilityFeature {
  id: string;
  name: string;
  type: string;
  lat: number;
  lng: number;
}

interface LeafletMapProps {
  incidents?: IncidentFeature[];
  roads?: RoadFeature[];
  facilities?: FacilityFeature[];
  routeCoordinates?: [number, number][]; // [ [lng, lat], ... ]
  standardRouteCoordinates?: [number, number][];
  onMarkerClick?: (incidentId: string) => void;
  center?: [number, number];
  zoom?: number;
  interactive?: boolean;
}

export const LeafletMap: React.FC<LeafletMapProps> = ({
  incidents = [],
  roads = [],
  facilities = [],
  routeCoordinates,
  standardRouteCoordinates,
  onMarkerClick,
  center = [27.1767, 78.0081],
  zoom = 14,
  interactive = true,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: center,
      zoom: zoom,
      zoomControl: interactive,
      dragging: interactive,
    });

    // Dark-matter styled OpenStreetMap tiles
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 19,
    }).addTo(map);

    const layerGroup = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;
    layerGroupRef.current = layerGroup;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Layers
  useEffect(() => {
    if (!mapInstanceRef.current || !layerGroupRef.current) return;
    const lg = layerGroupRef.current;
    lg.clearLayers();

    // 1. Draw Road Network Segments
    roads.forEach((road) => {
      const latlngs: L.LatLngExpression[] = road.coordinates.map((c) => [c[1], c[0]]);

      let color = "#22C55E"; // low
      if (road.isBlocked) color = "#EF4444";
      else if (road.riskScore >= 80) color = "#EF4444";
      else if (road.riskScore >= 55) color = "#F59E0B";
      else if (road.riskScore >= 30) color = "#EAB308";

      const polyline = L.polyline(latlngs, {
        color: color,
        weight: road.isBlocked ? 5 : 4,
        dashArray: road.isBlocked ? "6, 8" : undefined,
        opacity: road.isBlocked ? 0.9 : 0.7,
      });

      polyline.bindPopup(`
        <div style="font-family: monospace; font-size: 12px; color: #111;">
          <strong>${road.name}</strong><br/>
          Risk Score: <b>${road.riskScore.toFixed(1)}/100</b> (${road.riskLevel})<br/>
          Status: ${road.isBlocked ? "<span style='color:red;'>BLOCKED</span>" : "Open"}
        </div>
      `);
      lg.addLayer(polyline);
    });

    // 2. Draw Standard Route (Grey dashed) if present
    if (standardRouteCoordinates && standardRouteCoordinates.length > 0) {
      const stdPoints: L.LatLngExpression[] = standardRouteCoordinates.map((c) => [c[1], c[0]]);
      const stdLine = L.polyline(stdPoints, {
        color: "#64748B",
        weight: 4,
        dashArray: "8, 6",
        opacity: 0.8,
      });
      stdLine.bindPopup("<div style='font-family: monospace;'>Standard Shortest Path (Ignoring Hazards)</div>");
      lg.addLayer(stdLine);
    }

    // 3. Draw Risk-Aware Route (Cyan solid) if present
    if (routeCoordinates && routeCoordinates.length > 0) {
      const riskPoints: L.LatLngExpression[] = routeCoordinates.map((c) => [c[1], c[0]]);
      const riskLine = L.polyline(riskPoints, {
        color: "#22D3EE",
        weight: 6,
        opacity: 0.95,
      });
      riskLine.bindPopup("<div style='font-family: monospace; font-weight: bold; color: #0891B2;'>Hazard-Aware Safe Route</div>");
      lg.addLayer(riskLine);
    }

    // 4. Draw Facilities (Hospital, Shelter, Fire Station)
    facilities.forEach((fac) => {
      let iconEmoji = "🏥";
      if (fac.type === "shelter") iconEmoji = "⛺";
      if (fac.type === "fire_station") iconEmoji = "🚒";

      const facIcon = L.divIcon({
        className: "custom-facility-icon",
        html: `
          <div style="
            background: #111B2B;
            border: 2px solid #22D3EE;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            box-shadow: 0 0 10px rgba(34, 211, 238, 0.5);
          ">
            ${iconEmoji}
          </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      });

      const marker = L.marker([fac.lat, fac.lng], { icon: facIcon });
      marker.bindPopup(`
        <div style="font-family: monospace; font-size: 12px; color: #111;">
          <strong>${fac.name}</strong><br/>
          Type: ${fac.type.toUpperCase()}<br/>
          Critical Infrastructure
        </div>
      `);
      lg.addLayer(marker);
    });

    // 5. Draw Incidents
    incidents.forEach((inc) => {
      let color = "#22C55E";
      const s = inc.severity.toLowerCase();
      if (s === "critical" || s === "high") color = "#EF4444";
      else if (s === "medium") color = "#F59E0B";

      // Confidence controls pulse/ring border width
      const ringSize = inc.confidence >= 70 ? 14 : inc.confidence >= 40 ? 11 : 8;
      const ringOpacity = inc.confidence >= 70 ? 0.9 : 0.6;

      const incIcon = L.divIcon({
        className: "custom-incident-icon",
        html: `
          <div style="
            background: ${color};
            width: ${ringSize * 2}px;
            height: ${ringSize * 2}px;
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,${ringOpacity});
            box-shadow: 0 0 12px ${color};
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
          ">
            <span style="font-size: 9px; font-weight: bold; color: white;">🌊</span>
          </div>
        `,
        iconSize: [ringSize * 2, ringSize * 2],
        iconAnchor: [ringSize, ringSize],
      });

      const marker = L.marker([inc.lat, inc.lng], { icon: incIcon });
      marker.bindPopup(`
        <div style="font-family: monospace; font-size: 12px; color: #111; max-width: 220px;">
          <strong>${inc.title}</strong><br/>
          Severity: <b style="color: ${color}; text-transform: uppercase;">${inc.severity}</b><br/>
          TrustScore: <b>${inc.confidence.toFixed(1)}/100</b><br/>
          Status: ${inc.status}<br/>
          ${inc.isSimulated ? "<span style='color:purple; font-weight:bold;'>[SIMULATED]</span><br/>" : ""}
          <a href="/incidents/${inc.id}" style="color: #0891B2; text-decoration: underline; display: block; margin-top: 4px;">
            Inspect Full Evidence &rarr;
          </a>
        </div>
      `);

      if (onMarkerClick) {
        marker.on("click", () => onMarkerClick(inc.id));
      }

      lg.addLayer(marker);
    });
  }, [incidents, roads, facilities, routeCoordinates, standardRouteCoordinates]);

  return (
    <div className="relative w-full h-full min-h-[400px]">
      <div ref={mapContainerRef} className="w-full h-full rounded-lg overflow-hidden border border-borderDark" />
    </div>
  );
};
