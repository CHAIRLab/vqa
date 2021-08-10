package Graph;

import java.io.Serializable;
import java.util.HashMap;

public class SubGraph extends Graph implements Serializable{
	
	/**
	 * 
	 */
	private static final long serialVersionUID = -5248646795616116415L;

	private HashMap<Integer, Node> InNodes;				//	in-nodes of the graph
	private HashMap<Integer, Node> OutNodes;			//	out-nodes of the graph
	
	
	public SubGraph(){
		super();
	}
	
	public HashMap<Integer, Node> GetInNodes(){
		return this.InNodes;
	}
	
	public HashMap<Integer, Node> GetOutNodes(){
		return this.OutNodes;
	}

	public void SetInNodes(HashMap<Integer, Node> InNodes){
		this.InNodes = InNodes;
	}
	
	public void SetOutNodes(HashMap<Integer, Node> OutNodes){
		this.OutNodes = OutNodes;
	}
	
	public void Merges(SubGraph  sub){
		for(Node v : sub.GetNodeSet().values()){
			if(!this.GetNodeSet().values().contains(v)){
				this.InsNode(v);
			}
		}
		for(Edge e : sub.GetEdgeSet()){
			this.InsEdge(e);
		}
	}
}
