
# Let’s look at what a project management system where two agents work together to identify and schedule necessary meetings might look like. 
# The project management agent decides when meetings are needed, while a scheduling specialist handles the logistics of actually arranging them.

# First, let’s look at the tools available to our scheduling specialist. This agent needs to interact with calendars and create invites:


@register_tool()
def check_availability(
    action_context: ActionContext,
    attendees: List[str],
    start_date: str,
    end_date: str,
    duration_minutes: int,
    _calendar_api_key: str
) -> List[Dict]:
    """Find available time slots for all attendees."""
    return calendar_service.find_available_slots(...)

@register_tool()
def create_calendar_invite(
    action_context: ActionContext,
    title: str,
    description: str,
    start_time: str,
    duration_minutes: int,
    attendees: List[str],
    _calendar_api_key: str
) -> Dict:
    """Create and send a calendar invitation."""
    return calendar_service.create_event(...)







# The scheduling specialist is focused entirely on finding times and creating meetings:

scheduler_agent = Agent(
    goals=[
        Goal(
            name="schedule_meetings",
            description="""Schedule meetings efficiently by:
            1. Finding times that work for all attendees
            2. Creating and sending calendar invites
            3. Handling any scheduling conflicts"""
        )
    ],
...
)



# Now let’s look at our project management agent. 
# This agent focuses on project status and deciding when meetings are needed:


@register_tool()
def get_project_status(
    action_context: ActionContext,
    project_id: str,
    _project_api_token: str
) -> Dict:
    """Retrieve current project status information."""
    return project_service.get_status(...)

@register_tool()
def update_project_log(
    action_context: ActionContext,
    entry_type: str,
    description: str,
    _project_api_token: str
) -> Dict:
    """Record an update in the project log."""
    return project_service.log_update(...)

@register_tool()
def call_agent(
    action_context: ActionContext,
    agent_name: str,
    task: str
) -> Dict:
    """Delegate to a specialist agent."""
    # Implementation as shown in previous tutorial



# The project management agent uses these tools to monitor progress and arrange meetings when needed:


project_manager = Agent(
    goals=[
        Goal(
            name="project_oversight",
            description="""Manage project progress by:
            1. Getting the current project status
            2. Identifying when meetings are needed if there are issues in the project status log
            3. Delegating meeting scheduling to the "scheduler_agent" to arrange the meeting
            4. Recording project updates and decisions"""
        )
    ],
    ...
)



# This division of responsibilities keeps each agent focused on its core competency:

# The project manager understands project status and when meetings are needed
# The scheduler excels at finding available times and managing calendar logistics
# The call_agent tool allows seamless collaboration between them
# The call_agent Tool
# The call_agent tool manages several important aspects of agent interaction:

# Memory Isolation: Each invoked agent gets its own memory instance, preventing confusion between different agents’ conversation histories.

# Context Management: We carefully control what context properties are passed to the invoked agent, preventing infinite recursion while ensuring necessary resources are available.

# Result Handling: The tool extracts the final memory item as the result, providing a clean way to return information to the calling agent.

# Registering Agents
# To make this system work, we need to register our agents in the registry:



class AgentRegistry:
    def __init__(self):
        self.agents = {}
        
    def register_agent(self, name: str, run_function: callable):
        """Register an agent's run function."""
        self.agents[name] = run_function
        
    def get_agent(self, name: str) -> callable:
        """Get an agent's run function by name."""
        return self.agents.get(name)

# When setting up the system
registry = AgentRegistry()
registry.register_agent("scheduler_agent", scheduler_agent.run)

# Include registry in action context
action_context = ActionContext({
    'agent_registry': registry,
    # Other shared resources...
})



