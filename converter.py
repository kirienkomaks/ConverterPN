import numpy as np
import pntools.petrinet as pnt
import xml.etree.ElementTree as ET
import xml.dom.minidom
import sys
from graphviz import *
import time
from random import randint


class Edge:
    def __init__(self):
        self.id = (str(time.time())) + str(randint(0, 1000))
        self.source = None
        self.target = None
        self.type = 'normal'
        self.inscription = "1"
        self.net = None
        self.offsets = []  # offsets


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Converter(metaclass=Singleton):

    def __init__(self):
        self.places = 0
        self.transitions = 0
        self.matrix = []
        self.initial_marking = []
        self.places_ui = []
        self.transitions_ui = []
        self.petri_net = pnt.PetriNet()
        self.name = ""


    def __new__(cls, *args, **kwargs):
        print("Creating instance")
        return super(Converter, cls).__new__(cls)

    def read_pnm_np(self, file_name):
        f = open(file_name)
        triplets = f.read().split()

        self.places = int(triplets[0])
        self.transitions = int(triplets[1]) - 1

        # read matrix
        list_of_splited_lines = []
        for i in range(2, self.transitions + 2):
            splited_line = [char for char in triplets[i]]
            list_of_splited_lines.append(splited_line)

        self.matrix = np.array(list_of_splited_lines)

        # start points
        self.initial_marking = [char for char in triplets[self.transitions + 2]]
        name_line = triplets[self.transitions + 6]
        self.name = name_line.replace('"', '')
        print(self.name)
        f.close()

    @staticmethod
    def create_place(id, label, offset, position, marking):
        generated_place = pnt.Place()
        generated_place.id = id
        generated_place.label = label
        generated_place.offset = offset
        generated_place.position = position
        generated_place.marking = marking
        return generated_place

    @staticmethod
    def create_transition(id, label, offset, position):
        generated_transition = pnt.Transition()
        generated_transition.id = id
        generated_transition.label = label
        generated_transition.position = position
        generated_transition.offset = offset
        return generated_transition

    @staticmethod
    def create_edge(id, source, target, offsets):
        generated_edge = Edge()
        generated_edge.id = id
        generated_edge.source = source
        generated_edge.target = target
        generated_edge.offsets = offsets
        return generated_edge

    def read_pnml(self, filename):
        pn = pnt.PetriNet()

        doc = xml.dom.minidom.parse(filename)
        pn_id = doc.getElementsByTagName("net")[0].getAttribute("id")
        pn_name = doc.getElementsByTagName("net")[0].getAttribute("name")
        pn.id = pn_id
        pn.name = pn_name
        places = doc.getElementsByTagName("place")
        for p in places:
            place_id = p.getAttribute("id")
            place_name = p.getElementsByTagName("name")[0].getElementsByTagName("text")[0].firstChild.nodeValue
            marking = p.getElementsByTagName("initialMarking")[0].getElementsByTagName("text")[0].firstChild.nodeValue
            pn_place = self.create_place(place_id,place_name, [0, 0], [0, 0], marking)
            pn.places[pn_place.id] = pn_place

        transitions = doc.getElementsByTagName("transition")
        for t in transitions:

            transition_id = t.getAttribute("id")
            transition_name = t.getElementsByTagName("name")[0].getElementsByTagName("text")[0].firstChild.nodeValue
            pn_transition = self.create_transition(transition_id, transition_name, [0, 0], [0, 0])
            pn.transitions[pn_transition.id] = pn_transition

        edges = doc.getElementsByTagName("arc")
        for e in edges:
            edge_id = e.getAttribute("id")
            edge_source = e.getAttribute("source")
            edge_target = e.getAttribute("target")
            pn_edge = self.create_edge(int(edge_id), int(edge_source), int(edge_target), [0, 0])
            pn.edges.append(pn_edge)
        self.write_pnh(pn)

    @staticmethod
    def write_pnh(pn):
        f = open("generated_pnh\generated_" + pn.name + ".pnh", "w")
        f.write(str(len(pn.places)) + "\n")
        f.write(str(len(pn.transitions) + 1) + "\n")

        trans_count = len(pn.transitions)
        places_count = len(pn.places)
        places_names = ";Places="
        transition_names = ";Transitions="
        matrix = np.zeros((trans_count, places_count), dtype=int)
        marking = []

        iter_trans = 0
        for id, t in pn.transitions.items():
            tr_id = int(t.id)
            input_ids = []
            output_ids = []
            for e in pn.edges:
                if e.source == tr_id:
                    output_ids.append(e.target)
                elif e.target == tr_id:
                    input_ids.append(e.source)

            place_iter = 0
            for id, p in pn.places.items():
                for i in input_ids:
                    if int(id) == i:
                        matrix[iter_trans][place_iter] = -1
                for i in output_ids:
                    if int(id) == i:
                        matrix[iter_trans][place_iter] = 1
                place_iter += 1
            iter_trans += 1

        for i in matrix:
            for j in i:
                if j == -1:
                    f.write("x")
                else:
                    f.write(str(j))
            f.write("\n")

        for id, p in pn.places.items():
            marking.append(p.marking)
            places_names += (p.label + ";")
        for m in marking:
            f.write(m)
        f.write("\n")
        f.write("\n")
        f.write(places_names[:-1])
        for id, t in pn.transitions.items():
            transition_names += (t.label + ";")
        f.write("\n")
        f.write(transition_names[:-1])
        f.write("\n")
        f.write("\n")
        f.write(";Benchmark: " + '"' + pn.name + '"')
        f.close()

    @staticmethod
    def write_pnml(n, filename):
        snoopy = ET.Element('Snoopy')
        pnml = ET.SubElement(snoopy, 'pnml')
        net = ET.SubElement(pnml, 'net', id=n.id, name=n.name, type="IOPT")
        ...
        for id, p in n.places.items():
            place = ET.SubElement(net, 'place', id=p.id)
            place_name = ET.SubElement(place, 'name')
            place_name_text = ET.SubElement(place_name, 'text')
            place_name_text.text = p.label
            place_name_graphics = ET.SubElement(place_name, 'graphics')
            place_name_graphics_offset = ET.SubElement(place_name_graphics, 'offset')
            place_name_graphics_offset.attrib['x'] = str(p.offset[0] if p.offset is not None else 0)
            place_name_graphics_offset.attrib['y'] = str(p.offset[1] if p.offset is not None else 0)
            place_graphics = ET.SubElement(place, 'graphics')
            place_graphics_position = ET.SubElement(place_graphics, 'position')
            place_graphics_position.attrib['x'] = str(p.position[0] if p.position is not None else 0)
            place_graphics_position.attrib['y'] = str(p.position[1] if p.position is not None else 0)
            place_initial_marking = ET.SubElement(place, 'initialMarking')
            place_initial_marking_text = ET.SubElement(place_initial_marking, 'text')
            place_initial_marking_text.text = str(p.marking)

        for id, t in n.transitions.items():
            transition = ET.SubElement(net, 'transition', id=t.id)
            transition_name = ET.SubElement(transition, 'name')
            transition_name_text = ET.SubElement(transition_name, 'text')
            transition_name_text.text = t.label
            transition_name_graphics = ET.SubElement(transition_name, 'graphics')
            transition_name_graphics_offset = ET.SubElement(transition_name_graphics, 'offset')
            transition_name_graphics_offset.attrib['x'] = str(t.offset[0])
            transition_name_graphics_offset.attrib['y'] = str(t.offset[1])
            transition_graphics = ET.SubElement(transition, 'graphics')
            transition_graphics_position = ET.SubElement(transition_graphics, 'position')
            transition_graphics_position.attrib['x'] = str(t.position[0] if t.position is not None else 0)
            transition_graphics_position.attrib['y'] = str(t.position[1] if t.position is not None else 0)

        for e in n.edges:
            edge = ET.SubElement(net, 'arc', id=e.id, source=e.source, target=e.target)
            edge_type = ET.SubElement(edge, "type")
            edge_type.text = str(e.type)
            edge_graphics = ET.SubElement(edge, 'graphics')
            for i in range(0, len(e.offsets)):
                ET.SubElement(edge_graphics, 'offset', x=str(e.offsets[i][0]), y=str(e.offsets[i][1]))
            edge_inscription = ET.SubElement(edge, 'inscription')
            edge_inscription_value = ET.SubElement(edge_inscription, 'value')
            edge_inscription_value.text = str(e.inscription)

        tree = ET.ElementTree(element=snoopy)
        tree.write(filename, encoding="iso-8859-1", xml_declaration=True, method="xml")

    def create_pn(self):
        scale = 100
        places_position = {}
        transitions_position = {}
        list_of_edge_offsets = []
        with open('middle_output/graph.plain') as inputfile:
            names = [line.split() for line in inputfile if line.strip()]
            for i in range(len(names)):
                if names[i][0] == 'node' and i < self.places + 1:
                    places_position[names[i][1]] = [str(float(names[i][2]) * scale), str(float(names[i][3]) * scale)]
                elif names[i][0] == 'node' and i >= self.places + 1:
                    transitions_position[names[i][1]] = [str(float(names[i][2]) * scale),
                                                         str(float(names[i][3]) * scale)]
                elif names[i][0] == 'edge':
                    tab = [[names[i][1], names[i][2]]]
                    wsk = [6, 7]
                    if names[i][1][0] == 'P':
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        x_1 = float(places_position[names[i][1]][0])
                        y_1 = float(places_position[names[i][1]][1])
                        x = x - x_1
                        y = y - y_1
                        tab.append([x, y])
                        wsk[0] = len(names[i]) - 4
                        wsk[1] = len(names[i]) - 3
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        # need to clear floats
                        x_2 = float(transitions_position[names[i][2]][0])
                        y_2 = float(transitions_position[names[i][2]][1])
                        x = x - x_2
                        y = y - y_2
                        tab.append([x, y])
                    if names[i][1][0] == 't':
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        # need to clear floats
                        x_1 = float(transitions_position[names[i][1]][0])
                        y_1 = float(transitions_position[names[i][1]][1])
                        x = x - x_1
                        y = y - y_1
                        tab.append([x, y])

                        wsk[0] = len(names[i]) - 4
                        wsk[1] = len(names[i]) - 3
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale

                        x_2 = float(places_position[names[i][2]][0])
                        y_2 = float(places_position[names[i][2]][1])
                        x = x - x_2
                        y = y - y_2
                        tab.append([x, y])
                    list_of_edge_offsets.append(tab)

        ids = 0

        self.petri_net.id = '1'
        self.petri_net.name = self.name

        places_ids = {}
        transitions_ids = {}

        for p in range(self.places):
            place_name = 'P' + str(p)
            place = self.create_place(str(ids), place_name, [-10, 20], places_position[place_name], self.initial_marking[p])
            self.petri_net.places[place.id] = place
            places_ids[place_name] = str(ids)
            ids += 1

        for t in range(self.transitions):
            transition_name = 't' + str(t)
            transition = self.create_transition(str(ids), 't' + str(t), [-10, 20], transitions_position[transition_name])
            self.petri_net.transitions[transition.id] = transition
            transitions_ids[transition_name] = str(ids)
            ids += 1

        for i in range(0, len(list_of_edge_offsets)):
            if list_of_edge_offsets[i][0][0][0] == 'P':
                local_place = 'P' + str(list_of_edge_offsets[i][0][0][1:])
                local_transition = 't' + str(list_of_edge_offsets[i][0][1][1:])
                edge = self.create_edge(str(ids), places_ids[local_place], transitions_ids[local_transition],
                                        list_of_edge_offsets[i][1:])
                self.petri_net.edges.append(edge)
                ids += 1

            if list_of_edge_offsets[i][0][0][0] == 't':
                local_place = 'P' + str(list_of_edge_offsets[i][0][1][1:])
                local_transition = 't' + str(list_of_edge_offsets[i][0][0][1:])
                edge = self.create_edge(str(ids), transitions_ids[local_transition], places_ids[local_place],
                                        list_of_edge_offsets[i][1:])
                self.petri_net.edges.append(edge)
                ids += 1

        return self.petri_net

    def create_pn_UI(self):
        scale = 100
        places_position = {}
        transitions_position = {}
        list_of_edge_offsets = []
        with open('middle_output/graph.plain') as inputfile:
            names = [line.split() for line in inputfile if line.strip()]
            for i in range(len(names)):
                if names[i][0] == 'node' and i < self.places + 1:
                    places_position[names[i][1]] = [str(float(names[i][2]) * scale), str(float(names[i][3]) * scale)]
                elif names[i][0] == 'node' and i >= self.places + 1:
                    transitions_position[names[i][1]] = [str(float(names[i][2]) * scale), str(float(names[i][3]) * scale)]
                elif names[i][0] == 'edge':
                    tab = [[names[i][1], names[i][2]]]
                    wsk = [6, 7]
                    if names[i][1][0] == 'P':
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        x_1 = float(places_position[names[i][1]][0])
                        y_1 = float(places_position[names[i][1]][1])
                        x = x - x_1
                        y = y - y_1
                        tab.append([x, y])
                        wsk[0] = len(names[i]) - 4
                        wsk[1] = len(names[i]) - 3
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        # need to clear floats
                        x_2 = float(transitions_position[names[i][2]][0])
                        y_2 = float(transitions_position[names[i][2]][1])
                        x = x - x_2
                        y = y - y_2
                        tab.append([x, y])
                    if names[i][1][0] == 't':
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale
                        # need to clear floats
                        x_1 = float(transitions_position[names[i][1]][0])
                        y_1 = float(transitions_position[names[i][1]][1])
                        x = x - x_1
                        y = y - y_1
                        tab.append([x, y])

                        wsk[0] = len(names[i]) - 4
                        wsk[1] = len(names[i]) - 3
                        x = float(names[i][wsk[0]]) * scale
                        y = float(names[i][wsk[1]]) * scale

                        x_2 = float(places_position[names[i][2]][0])
                        y_2 = float(places_position[names[i][2]][1])
                        x = x - x_2
                        y = y - y_2
                        tab.append([x, y])
                    list_of_edge_offsets.append(tab)

        ids = 0
        self.petri_net.id = '1'
        self.petri_net.name = self.petri_net.id

        places_ids = {}
        transitions_ids = {}

        for p in range(self.places):
            place_name = self.places_ui[p][0]
            place = self.create_place(str(ids), place_name, [-10, 20], places_position[place_name], self.places_ui[p][1])
            self.petri_net.places[place.id] = place
            places_ids[place_name] = str(ids)
            ids += 1

        for t in range(self.transitions):
            transition_name = self.transitions_ui[t][0]
            transition = self.create_transition(str(ids), transition_name, [-10, 20], transitions_position[transition_name])
            self.petri_net.transitions[transition.id] = transition
            transitions_ids[transition_name] = str(ids)
            ids += 1

        for i in range(0, len(list_of_edge_offsets)):
            if list_of_edge_offsets[i][0][0][0] == 'P':
                local_place = 'P' + str(list_of_edge_offsets[i][0][0][1:])
                local_transition = 't' + str(list_of_edge_offsets[i][0][1][1:])
                edge = self.create_edge(str(ids), places_ids[local_place], transitions_ids[local_transition],
                                        list_of_edge_offsets[i][1:])
                self.petri_net.edges.append(edge)
                ids += 1

            if list_of_edge_offsets[i][0][0][0] == 't':
                local_place = 'P' + str(list_of_edge_offsets[i][0][1][1:])
                local_transition = 't' + str(list_of_edge_offsets[i][0][0][1:])
                edge = self.create_edge(str(ids), transitions_ids[local_transition], places_ids[local_place],
                                        list_of_edge_offsets[i][1:])
                self.petri_net.edges.append(edge)
                ids += 1

        return self.petri_net

    def graphviz_formatter(self):
        global places
        dot = Digraph()
        dot.format = 'plain'
        dot.graph_attr['rankdir'] = 'BT'
        for x in range(self.places):
            dot.node('P' + str(x))

        for x in range(self.transitions):
            dot.node('t' + str(x))

        for i in range(self.transitions):
            for j in range(self.places):
                if self.matrix[i][j] == '1':
                    dot.edge('t' + str(i), 'P' + str(j))
                if self.matrix[i][j] == 'x':
                    dot.edge('P' + str(j), 't' + str(i))

        dot.render('middle_output/graph')
        self.render_pdf(dot)

    def graphviz_formatter_ui(self, places_ui, transitions_ui):
        dot = Digraph()
        dot.format = 'plain'
        # dot.graph_attr['rankdir'] = 'BT'
        self.places_ui = places_ui
        self.transitions_ui = transitions_ui
        self.initial_marking = []
        for p in places_ui:
            self.initial_marking.append(p[1])
            dot.node(p[0])
        for t in transitions_ui:

            dot.node(t[0])
            for ie in t[1]:
                dot.edge(ie, t[0])
            for oe in t[2]:
                dot.edge(t[0], oe)
        dot.render('middle_output/graph')
        self.render_pdf(dot)

    def render_pdf(self, dot):
        dot.format = 'pdf'
        dot.render('middle_output/graph')


if __name__ == '__main__':
    converter = Converter()
    if len(sys.argv) < 2:
        print("Error: Please, execute program with args")
    elif int(sys.argv[1]) == 0:
        print("Converter PNH -> PNML")
        # PNM Reader

        output_path = "pnml\\"
        converter.read_pnm_np(sys.argv[2])

        # Create graph
        converter.graphviz_formatter()

        # Petri Net creation
        petri_net = converter.create_pn()

        graph_name = sys.argv[2].__str__()[4:-4]
        print(graph_name)
        converter.write_pnml(petri_net, output_path + "generated_" + graph_name + ".pnml")
    elif int(sys.argv[1]) == 1:
        print("Converter PNML -> PNH")
        converter.read_pnml(sys.argv[2])

