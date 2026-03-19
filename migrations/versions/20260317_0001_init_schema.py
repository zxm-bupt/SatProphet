"""Initial schema for satellite, tle, and ground track."""

from alembic import op
import sqlalchemy as sa


revision = "20260317_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "satellite",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("norad_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_tracked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_satellite_norad_id", "satellite", ["norad_id"], unique=True)
    op.create_index("ix_satellite_is_tracked", "satellite", ["is_tracked"], unique=False)

    op.create_table(
        "tle_record",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("satellite_id", sa.Integer(), sa.ForeignKey("satellite.id"), nullable=False),
        sa.Column("epoch", sa.DateTime(timezone=True), nullable=False),
        sa.Column("line1", sa.String(length=128), nullable=False),
        sa.Column("line2", sa.String(length=128), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False, server_default=sa.text("'spacetrack'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tle_record_satellite_id", "tle_record", ["satellite_id"], unique=False)
    op.create_index("ix_tle_record_epoch", "tle_record", ["epoch"], unique=False)
    op.create_unique_constraint("uq_tle_satellite_epoch", "tle_record", ["satellite_id", "epoch"])

    op.create_table(
        "satellite_ground_track",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("satellite_id", sa.Integer(), sa.ForeignKey("satellite.id"), nullable=False),
        sa.Column("latitude_deg", sa.Float(), nullable=False),
        sa.Column("longitude_deg", sa.Float(), nullable=False),
        sa.Column("altitude_km", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_unique_constraint("uq_satellite_ground_track_satellite", "satellite_ground_track", ["satellite_id"])

    op.execute("ALTER TABLE satellite_ground_track ADD COLUMN ground_point GEOGRAPHY(POINT, 4326)")
    op.execute(
        "CREATE INDEX ix_satellite_ground_track_ground_point ON satellite_ground_track USING GIST (ground_point)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_satellite_ground_track_ground_point")
    op.drop_constraint("uq_satellite_ground_track_satellite", "satellite_ground_track", type_="unique")
    op.drop_table("satellite_ground_track")

    op.drop_constraint("uq_tle_satellite_epoch", "tle_record", type_="unique")
    op.drop_index("ix_tle_record_epoch", table_name="tle_record")
    op.drop_index("ix_tle_record_satellite_id", table_name="tle_record")
    op.drop_table("tle_record")

    op.drop_index("ix_satellite_is_tracked", table_name="satellite")
    op.drop_index("ix_satellite_norad_id", table_name="satellite")
    op.drop_table("satellite")
