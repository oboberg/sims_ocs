from sqlalchemy import Column, Float, Index, Integer, String, Table
from sqlalchemy.types import DATETIME
from sqlalchemy import DDL, event, ForeignKeyConstraint

__all__ = ["create_field", "create_observation_exposures", "create_observation_history",
           "create_session", "create_slew_history", "create_slew_final_state", "create_slew_initial_state",
           "create_target_exposures", "create_target_history"]

def create_field(metadata):
    """Create Field table.

    This function creates the Field table from the sky tesellation.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The Field table object.
    """
    table = Table("Field", metadata,
                  Column("fieldId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("fov", Float, nullable=False),
                  Column("ra", Float, nullable=False),
                  Column("dec", Float, nullable=False),
                  Column("gl", Float, nullable=False),
                  Column("gb", Float, nullable=False),
                  Column("el", Float, nullable=False),
                  Column("eb", Float, nullable=False))

    Index("field_fov", table.c.fieldId, table.c.fov)
    Index("fov_gl_gb", table.c.fov, table.c.gl, table.c.gb)
    Index("fov_el_eb", table.c.fov, table.c.el, table.c.eb)
    Index("fov_ra_dec", table.c.fov, table.c.ra, table.c.dec)

    return table

def create_observation_exposures(metadata):
    """Create ObsExposures table.

    This function creates the ObsExposures table from the observation exposures.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
      The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
      The ObsExposure table object.
    """
    table = Table("ObsExposures", metadata,
                  Column("exposureId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("exposureNum", Integer, nullable=False),
                  Column("exposureStartTime", Float, nullable=False),
                  Column("exposureTime", Float, nullable=False),
                  Column("ObsHistory_observationId", Integer, nullable=False))

    Index("obs_expId_expNum", table.c.exposureId, table.c.exposureNum)
    Index("fk_ObsHistory_observationId", table.c.ObsHistory_observationId)

    return table

def create_observation_history(metadata):
    """Create ObsHistory table.

    This function creates the ObsHistory table for tracking all the observations performed
    by the Sequencer in the simulation run.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The ObsHistory table object.
    """
    table = Table("ObsHistory", metadata,
                  Column("observationId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column('night', Integer, nullable=False),
                  Column('observationStartTime', Float, nullable=False),
                  Column('observationStartMJD', Float, nullable=False),
                  Column('observationStartLST', Float, nullable=False,
                         doc="The Local Sidereal Time at observation start"),
                  Column('TargetHistory_targetId', Integer, nullable=False),
                  Column("Field_fieldId", Integer, nullable=False),
                  Column("filter", String(1), nullable=False),
                  Column("ra", Float, nullable=False),
                  Column("dec", Float, nullable=False),
                  Column("angle", Float, nullable=False),
                  Column("numExposures", Integer, nullable=False),
                  Column("visitTime", Float, nullable=False),
                  Column("visitExposureTime", Float, nullable=False),
                  ForeignKeyConstraint(["Field_fieldId"], ["Field.fieldId"]),
                  ForeignKeyConstraint(["TargetHistory_targetId"], ["TargetHistory.targetId"]))

    Index("o_filter", table.c.filter)
    Index("fk_ObsHistory_Session1", table.c.Session_sessionId)
    Index("fk_ObsHistory_Field1", table.c.Field_fieldId)
    Index("fk_ObsHistory_Target1", table.c.TargetHistory_targetId)

    return table

def create_session(metadata, autoincrement=True):
    """Create Session table.

    This function creates the Session table for tracking the various simulations run. For MySQL, it adds
    a post-create command to set the lower limit of the auto increment value.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.
    autoincrement : bool
        A flag to set auto incrementing on the sessionID column.

    Returns
    -------
    sqlalchemy.Table
        The Session table object.
    """
    table = Table("Session", metadata,
                  Column("sessionId", Integer, primary_key=True, autoincrement=autoincrement, nullable=False),
                  Column("sessionUser", String(80), nullable=False),
                  Column("sessionHost", String(80), nullable=False),
                  Column("sessionDate", DATETIME, nullable=False),
                  Column("version", String(25), nullable=True),
                  Column("runComment", String(200), nullable=True))

    Index("s_host_user_date_idx", table.c.sessionUser, table.c.sessionHost, table.c.sessionDate, unique=True)

    alter_table = DDL("ALTER TABLE %(table)s AUTO_INCREMENT=1000;")
    event.listen(table, 'after_create', alter_table.execute_if(dialect='mysql'))

    return table

def create_slew_history(metadata):
    """Create SlewHistory table.

    This function creates the SlewHistory table for tracking all the general slew information
    performed by the observatory.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The SlewHistory table object.
    """
    table = Table("SlewHistory", metadata,
                  Column("slewCount", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("startDate", Float, nullable=False),
                  Column("endDate", Float, nullable=False),
                  Column("slewTime", Float, nullable=False),
                  Column("slewDistance", Float, nullable=False),
                  Column("ObsHistory_observationId", Integer, nullable=False),
                  ForeignKeyConstraint(["ObsHistory_observationId"], ["ObsHistory.observationId"]))

    Index("fk_SlewHistory_ObsHistory1", table.c.ObsHistory_observationId)

    return table

def create_slew_final_state(metadata):
    """Create the SlewFinalState tables.

    This function creates the SlewFinalState table for tracking the state of the observatory after slewing.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The SlewFinalState table object.
    """
    return create_slew_state("SlewFinalState", metadata)

def create_slew_initial_state(metadata):
    """Create the SlewInitialState tables.

    This function creates the SlewInitialState table for tracking the state of the observatory before slewing.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The SlewInitialState table object.
    """
    return create_slew_state("SlewInitialState", metadata)

def create_slew_state(name, metadata):
    """Create one of the SlewState tables.

    This function creates on of the SlewState tables.

    Parameters
    ----------
    name : str
        The name of the slew state table.
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        One of the SlewState table objects.
    """
    table = Table(name, metadata,
                  Column("slewStateId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("slewStateDate", Float, nullable=False),
                  Column("targetRA", Float, nullable=False),
                  Column("targetDec", Float, nullable=False),
                  Column("tracking", String(10), nullable=False),
                  Column("altitude", Float, nullable=False),
                  Column("azimuth", Float, nullable=False),
                  Column("paraAngle", Float, nullable=False),
                  Column("domeAlt", Float, nullable=False),
                  Column("domeAz", Float, nullable=False),
                  Column("telAlt", Float, nullable=False),
                  Column("telAz", Float, nullable=False),
                  Column("rotTelPos", Float, nullable=False),
                  Column("rotSkyPos", Float, nullable=False),
                  Column("filter", String(1), nullable=False),
                  Column("SlewHistory_slewCount", Integer, nullable=False))

    Index("fk_{}_SlewHistory1".format(name), table.c.SlewHistory_slewCount)

    return table

def create_target_exposures(metadata):
    """Create TargetExposures table.

    This function creates the TargetExposures table from the target exposures.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
      The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
      The Target Exposure table object.
    """
    table = Table("TargetExposures", metadata,
                  Column("exposureId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("exposureNum", Integer, nullable=False),
                  Column("exposureTime", Float, nullable=False),
                  Column("TargetHistory_targetId", Integer, nullable=False))

    Index("expId_expNum", table.c.exposureId, table.c.exposureNum)
    Index("fk_TargetHistory_targetId", table.c.TargetHistory_targetId)

    return table

def create_target_history(metadata):
    """Create TargetHistory table.

    This function creates the TargetHistory table for tracking all the requested targets from
    the Scheduler in the simulation run.

    Parameters
    ----------
    metadata : sqlalchemy.MetaData
        The database object that collects the tables.

    Returns
    -------
    sqlalchemy.Table
        The TargetHistory table object.
    """
    table = Table("TargetHistory", metadata,
                  Column("targetId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Session_sessionId", Integer, primary_key=True, autoincrement=False, nullable=False),
                  Column("Field_fieldId", Integer, nullable=False),
                  Column("filter", String(1), nullable=False),
                  Column("ra", Float, nullable=False),
                  Column("dec", Float, nullable=False),
                  Column("angle", Float, nullable=False),
                  Column("numExposures", Integer, nullable=False),
                  Column("requestedExpTime", Float, nullable=False))

    Index("t_filter", table.c.filter)
    Index("fk_TargetHistory_Session1", table.c.Session_sessionId)
    Index("fk_TargetHistory_Field1", table.c.Field_fieldId)

    return table
