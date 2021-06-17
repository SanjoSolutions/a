import random


class A:
    def explore(self, environment, database, number_of_explorations):
        for exploration_number in range(1, number_of_explorations + 1):
            self.do_unexplored_action(environment, database)
            if environment.is_done():
                environment.reset()

    def do_unexplored_action(self, environment, database):
        state_before_action = environment.get_state()
        action = self.pick_unexplored_action(environment, database)
        environment.do_action(action)
        state_after_action = environment.get_state()
        database.store(state_before_action, action, state_after_action)

    def pick_unexplored_action(self, environment, database):
        available_actions = environment.get_available_actions()
        if len(available_actions) == 0:
            raise ValueError('Expected at least one available action. Received zero available actions.')
        state = environment.get_state()
        explored_actions = database.query_explored_actions(state)
        unexplored_actions = available_actions - explored_actions
        if len(unexplored_actions) >= 1:
            actions_to_choose_from = unexplored_actions
            action = random.choice(tuple(actions_to_choose_from))
            database.store_unexplored_actions_count(state, len(unexplored_actions) - 1)
        else:
            action = max(
                available_actions,
                key=lambda action: self.determine_query_total_known_unexplored_actions_count(
                    database, state, action
                )
            )
        return action

    def determine_query_total_known_unexplored_actions_count(self, database, state, action):
        resulting_state = database.query_state(state, action)
        if resulting_state is not None:
            return database.query_total_known_unexplored_actions_count(
                resulting_state
            )
        else:
            return 0  # to make it work well with the max function, where this function is used.

    def evaluate(self, environment, database, determine_metric_value):
        state = tuple(environment.get_state())
        outcome = database.query_state_with_highest_metric_value(determine_metric_value)
        paths = [
            [outcome]
        ]
        while len(paths) >= 1:
            next_paths = []
            for path in paths:
                state_and_action_pairs = database.query_state_and_action_pairs_which_lead_to_state(path[0])
                for state_and_action_pair in state_and_action_pairs:
                    next_path = list(state_and_action_pair) + path
                    if next_path[0] == state:
                        path_to_outcome = next_path
                        actions_to_outcome = self.retrieve_actions_from_path(path_to_outcome)
                        self.do_actions(environment, actions_to_outcome)
                        return path_to_outcome
                    next_paths.append(next_path)
                paths = next_paths
        return None

    def retrieve_actions_from_path(self, path):
        actions = []
        for index in range(1, len(path) - 1, 2):
            action = path[index]
            actions.append(action)
        return actions

    def do_actions(self, environment, actions):
        for action in actions:
            environment.do_action(action)
