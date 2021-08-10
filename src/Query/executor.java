package Query;

import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;
import java.util.Vector;

import org.json.JSONException;

import Graph.Edge;
import Graph.Graph;
import Graph.Node;
import FileOpe.ReadFile;


public class executor {

	public Graph patternGenLength(int d) {
		Graph p = new Graph();
		return p;
	}

	public Graph qa_patternGen() {
		Graph p = new Graph();

		Node v1 = new Node("1", "tile", null, null);
		Node v2 = new Node("2", "wall", null, null);
		Node v3 = new Node("3", "*", null, null);

		p.InsNode(v1);
		p.InsNode(v2);
		p.InsNode(v3);
				

		Edge e1 = new Edge();
		Edge e2 = new Edge();

		e1.SetFromNode(v1);
		e1.SetToNode(v2);
		e2.SetFromNode(v1);
		e2.SetToNode(v3);

		e1.setType("on");
		e2.setType("color");
		p.InsEdge(e1);
		p.InsEdge(e2);

		return p;
	}

	public Graph qa_graphGen() {
		Graph p = new Graph();

		Node v1 = new Node("1", "tile", null, null);
		Node v2 = new Node("2", "wall", null, null);
		Node v3 = new Node("3", "red", null, null);

		p.InsNode(v1);
		p.InsNode(v2);
		p.InsNode(v3);

		Edge e1 = new Edge();
		Edge e2 = new Edge();

		e1.SetFromNode(v1);
		e1.SetToNode(v2);
		e2.SetFromNode(v1);
		e2.SetToNode(v3);

		e1.setType("on");
		e2.setType("color");
		p.InsEdge(e1);
		p.InsEdge(e2);

		return p;
	}
	

	public static void main(String[] args) throws FileNotFoundException, UnsupportedEncodingException, JSONException {

		executor exe = new executor();

		Vector<Node> core_1 = new Vector<Node>();
		Vector<Node> core_2 = new Vector<Node>();
		Vector<Node> in_1 = new Vector<Node>();
		Vector<Node> in_2 = new Vector<Node>();
		Vector<Node> out_1 = new Vector<Node>();
		Vector<Node> out_2 = new Vector<Node>();
		Node n1 = null;
		Node n2 = null;
		
		
		String question = "What color is the bottle on the sink?";
		question = question.toLowerCase();
		System.out.println("question: "+question);
		
		ReadFile rf = new ReadFile();
		Graph G = rf.readJsonFromSG("src//Data//scene_graph//131090.json");  //scene graph
//		G.Display();  //œ‘ ægraph
		
		Graph P = rf.readJsonFromWG("src//Data//word_graph//131090.json");  // word graph
//		P.Display();
		
		VF2 vf2 = new VF2(G, P);
		vf2.Match(core_1, core_2, in_1, in_2, out_1, out_2, n1, n2, G, P);
		

	}
}
