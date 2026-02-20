
# While tools provide specific functions our agent can use, 
# sometimes we need to extend the agent’s core behavior in more fundamental ways. 
# The Capability pattern allows us to modify multiple aspects of the agent loop while
# keeping the core logic clean and maintainable.

# The idea behind the Capability pattern is to encapsulate specific adaptations of the agent loop inside of a class. 
# This class can be plugged in to modify the behavior of the agent loop without modifying the loop code itself. 
# Agent’s that need more specialized agent loop behavior can be composed by adding capabilities to the agent. 
# The Capability has a lifecycle that begins when the agent loop is about to start and ends when the agent loop is about to terminate. 
# A Capability might open a database connection, log prompts being sent to the LLM, or add metadata to the agent’s responses.

# Let’s explore this pattern by implementing something seemingly simple but powerful:
#  making our agent aware of time. An agent that understands time can make better decisions about scheduling, 
#  deadlines, and time-sensitive tasks.

# The Capability Pattern
# A Capability can interact with the agent loop at multiple points. 
# Looking at our Agent class, we can see these interaction points:



def run(self, user_input: str, memory=None, action_context_props=None):

    ... existing code ...
    
    # Initialize capabilities
    for capability in self.capabilities:
        capability.init(self, action_context)
        
    while True:
        # Start of loop capabilities
        can_start_loop = reduce(lambda a, c: c.start_agent_loop(self, action_context),
                              self.capabilities, False)

        ... existing code ...
        
        # Construct prompt with capability modifications
        prompt = reduce(lambda p, c: c.process_prompt(self, action_context, p),
                      self.capabilities, base_prompt)

        ... existing code ...
        
        # Process response with capabilities
        response = reduce(lambda r, c: c.process_response(self, action_context, r),
                        self.capabilities, response)

        ... existing code ...
        
        # Process action with capabilities
        action = reduce(lambda a, c: c.process_action(self, action_context, a),
                      self.capabilities, action)
        
        ... existing code ...
        
        # Process result with capabilities
        result = reduce(lambda r, c: c.process_result(self, action_context, response,
                                                     action_def, action, r),
                       self.capabilities, result)

        ... existing code ...
        
        # End of loop capabilities
        for capability in self.capabilities:
            capability.end_agent_loop(self, action_context)