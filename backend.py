from sqlalchemy import create_engine, Column, Text, Boolean, Integer, String, DateTime, func,ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import datetime
from sqlalchemy import func
from datetime import datetime, timedelta
from ariadne import gql, QueryType, MutationType, make_executable_schema, load_schema_from_path, graphql_sync
from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL


Base = declarative_base()

class DIMUser(Base):
    __tablename__ = 'dim_users'  # Use lowercase to match PostgreSQL's default behavior
    
    id = Column(Integer, primary_key=True)
    user_name = Column(String(255))
    created_at = Column(TIMESTAMP, nullable=False)
    
class DIMPlans(Base):
    __tablename__ = 'dim_plans' 
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, nullable=False)

class Activity(Base):
    __tablename__ = 'activity'  # Table name in lowercase
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('dim_users.id'))  # Correct FK reference to 'dim_users.id'
    plan_id = Column(Integer, ForeignKey('dim_plans.id'))  # Correct FK reference to 'dim_plans.id'
    event_type = Column(String(255), nullable=False)
    task_content = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False)

# Connect to your PostgreSQL database
DATABASE_URL = "postgresql://postgres:password@localhost:5432/daily_planning"
engine = create_engine(DATABASE_URL)
# Base.metadata.drop_all(bind=engine)
Session = sessionmaker(bind=engine)

# define resolvers
# Create QueryType and MutationType instances
query = QueryType()
mutation = MutationType()


@query.field("findPlanOnSpecificDay")
def resolve_find_plan(_, info, userId, day):
    """
    Finds activities for a specific user on a specific day.
    
    :param _: Unused parameter, convention for GraphQL resolvers.
    :param info: Provides context for the GraphQL query (unused here).
    :param userId: The ID of the user to find activities for.
    :param day: The day to find activities on, provided as 'YYYY-MM-DD'.
    :return: A list of Activity objects for the user on the specified day.
    """
    # Convert the input day string to a datetime object representing the start and end of the day
    day_start = datetime.strptime(day, "%Y-%m-%d")
    day_end = day_start + timedelta(days=1)

    # Create a new database session
    session = Session()

    try:
        # Query for activities by a specific user within the specified day
        activities = session.query(Activity)\
                            .filter(Activity.user_id == userId)\
                            .filter(Activity.created_at >= day_start)\
                            .filter(Activity.created_at < day_end)\
                            .all()
    finally:
        # Ensure the session is closed after the operation
        session.close()

    return activities
    
    
@mutation.field("insertNewPlan")
def resolve_insert_new_plan(_, info, userId, createdAt, eventType, taskContent):
    """
    Inserts a new plan linked to a user and creates an initial activity for the plan.

    Parameters:
    - userId (ID!): The ID of the user the new plan is associated with.
    - createdAt (String!): The creation time for the plan and activity, provided as a string.
    - eventType (String!): The type of the initial activity.
    - taskContent (String!): The content of the task for the initial activity.

    Returns:
    - A dictionary with 'plan_id' of the newly created Plan.
    """
    created_at_datetime = datetime.strptime(createdAt, "%Y-%m-%d %H:%M:%S")
    
    session = Session()
    try:
        # Create and add a new Plan to the session
        new_plan = DIMPlans(created_at=created_at_datetime)
        session.add(new_plan)
        session.flush()  # Ensures the new plan gets an ID assigned

        # Create and add a new Activity linked to the new plan
        new_activity = Activity(
            user_id=userId,
            plan_id=new_plan.id,  # Correctly access new_plan's id attribute
            event_type=eventType,
            task_content=taskContent,
            created_at=created_at_datetime
        )
        session.add(new_activity)

        session.commit()
        # Correctly returning the ID of the new plan using dot notation
        return {"plan_id": new_plan.id}  
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")  # It's better to log errors
        return {"error": "Failed to insert new plan."}
    finally:
        session.close()
 


# Load schema from .graphql file
type_defs = load_schema_from_path("schema.graphql")
# Make the executable schema
schema = make_executable_schema(type_defs, query, mutation)
graphql_app = GraphQL(schema, debug=True)