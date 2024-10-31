
import re

class State:
    def __init__(self, name, is_final=False, final_weight=0.0):
        self.name = name
        self.is_final = is_final
        self.final_weight = final_weight
        self.transitions = []

    def add_transition(self, input_symbol, output_symbol, target_state, weight=1.0):
        print(f"Adding transition: {self.name} --{input_symbol}/{output_symbol}, {weight}--> {target_state.name}")
        self.transitions.append((input_symbol, output_symbol, target_state, weight))


class FST:
    def __init__(self):
        self.states = {}
        self.start_state = None
        print("Initialized FST")

    def add_state(self, name, is_final=False, final_weight=0.0):
        if name not in self.states:
            state = State(name, is_final, final_weight)
            self.states[name] = state
            if self.start_state is None:
                self.start_state = state
                print(f"Set start state: {name}")
            print(f"Added state: {name}, is_final={is_final}, final_weight={final_weight}")
        else:
            print(f"Already {name} already added")

    def add_transition(self, from_state_name, input_symbol, output_symbol, to_state_name, weight=1.0):
        if from_state_name not in self.states:
            self.add_state(from_state_name)
        if to_state_name not in self.states:
            self.add_state(to_state_name)
        from_state = self.states.get(from_state_name)
        to_state = self.states.get(to_state_name)
        from_state.add_transition(input_symbol, output_symbol, to_state, weight)

    def transduce(self, input_string):
        transduce_node(self, self.start_state, input_string)

    # assume no epsilon loops
    def transduce_node(self, node, input_string):
        new_node_list = []
        if input_string == "" and node.is_final:
            yield "", node.final_weight
        else:
            new_node_list = [arc + (input_string[1:],) for arc in node.transitions if arc[0] == input_string[0]]
        epsilon_list = [arc + (input_string,) for arc in node.transitions if arc[0] == "0"]

        for _, output, target, weight, input_rest in new_node_list + epsilon_list:
            for rec_output, total_weight in self.transduce_node(target, input_rest):
                yield output + rec_output, weight + total_weight


    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            transition_pattern = re.compile(r'^(\d+)\s+(\d+)\s+(\w+)\s+(\w+)(\s+\d+(\.\d+)?)?$')
            final_state_pattern = re.compile(r'^(\d+)(\s+\d+(\.\d+)?)?$')
            
            print(f"Loading FST from file: {filename}")
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                transition_match = transition_pattern.match(line)
                final_state_match = final_state_pattern.match(line)
                
                if transition_match:
                    from_state = transition_match.group(1)
                    to_state = transition_match.group(2)
                    input_symbol = transition_match.group(3)
                    output_symbol = transition_match.group(4)
                    weight = float(transition_match.group(5)) if transition_match.group(5) else 1.0
                    print(f"Adding transition from file: {from_state} -> {to_state}, {input_symbol}/{output_symbol}, weight: {weight}")
                    self.add_transition(from_state, input_symbol, output_symbol, to_state, weight)
                elif final_state_match:
                    state_name = final_state_match.group(1)
                    weight = float(final_state_match.group(2)) if final_state_match.group(2) else 0.0
                    print(f"Marking state as final from file: {state_name}, weight: {weight}")
                    self.add_state(state_name, is_final=True, final_weight=weight)
                else:
                    raise ValueError(f"Invalid line in FST file: {line}")

    def __repr__(self):
        return f"FST(states={list(self.states.keys())}, start_state={self.start_state})"

# Example usage
if __name__ == "__main__":
    fst = FST()
    # Load FST from a file in simplified notation
    # Example file content:
    # 0 1 a x 0.5
    # 0 1 b y 1.5
    # 1 2 c z 2.5
    # 2 3.5
    fst.load_from_file("fst_definition.txt")

    input_string = "abc"
    try:
        output, total_weight = fst.process(input_string)
        print(f"Input: {input_string}, Output: {output}, Total Weight: {total_weight}")
    except ValueError as e:
        print(f"Error: {e}")
