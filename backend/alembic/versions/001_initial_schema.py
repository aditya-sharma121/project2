"""Initial schema with PostGIS and UUID

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='citizen'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Incidents
    op.create_table(
        'incidents',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('incident_type', sa.String(length=100), nullable=False, server_default='urban_flooding'),
        sa.Column('reported_severity', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('ai_severity', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='reported'),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_simulated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_incidents_status_created', 'incidents', ['status', 'created_at'])
    op.create_index('idx_incidents_coords', 'incidents', ['latitude', 'longitude'])

    # Evidence
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('incident_id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('image_url', sa.String(length=1024), nullable=False),
        sa.Column('image_hash', sa.String(length=64), nullable=False),
        sa.Column('phash', sa.String(length=64), nullable=False),
        sa.Column('visible_water', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ai_confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ai_result', sa.JSON(), nullable=True),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_evidence_incident_uploaded', 'evidence', ['incident_id', 'uploaded_at'])
    op.create_index('ix_evidence_hash', 'evidence', ['image_hash'])
    op.create_index('ix_evidence_phash', 'evidence', ['phash'])

    # Verifications (Append-only)
    op.create_table(
        'verifications',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('incident_id', sa.String(length=36), nullable=False),
        sa.Column('verified_by', sa.String(length=36), nullable=True),
        sa.Column('geographic_agreement', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('temporal_agreement', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('visual_quality', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('independent_source_quality', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('trust_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_label', sa.String(length=50), nullable=False, server_default='Unverified'),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_verifications_incident_created', 'verifications', ['incident_id', 'created_at'])

    # Road Segments
    op.create_table(
        'road_segments',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('road_class', sa.String(length=50), nullable=False, server_default='primary'),
        sa.Column('start_node', sa.String(length=50), nullable=False),
        sa.Column('end_node', sa.String(length=50), nullable=False),
        sa.Column('distance_m', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='low'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_road_risk_blocked', 'road_segments', ['risk_score', 'is_blocked'])

    # Facilities
    op.create_table(
        'facilities',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('facility_type', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='operational'),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_facilities_type', 'facilities', ['facility_type'])

    # Routes
    op.create_table(
        'routes',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('origin_lat', sa.Float(), nullable=False),
        sa.Column('origin_lng', sa.Float(), nullable=False),
        sa.Column('dest_lat', sa.Float(), nullable=False),
        sa.Column('dest_lng', sa.Float(), nullable=False),
        sa.Column('distance_m', sa.Float(), nullable=False),
        sa.Column('total_risk', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('avoided_segments', sa.JSON(), nullable=True),
        sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326), nullable=True),
        sa.Column('computed_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('routes')
    op.drop_table('facilities')
    op.drop_table('road_segments')
    op.drop_table('verifications')
    op.drop_table('evidence')
    op.drop_table('incidents')
    op.drop_table('users')
