package Graph;

import java.io.Serializable;

public class Edge implements Serializable{

	private static final long serialVersionUID = -6866526224292480860L;

	private Node fromNode;	// 开始节点 (弧尾 tail)
	private Node toNode;			//	终止节点 (弧头 head)
	private Edge hlink;				//	指向弧头相同的下一条弧
	private Edge tlink; 				//	指向弧尾相同的下一条弧
	private String type;               //设置边的属性
	
	/**
	 * CONSTRUCTOR
	 * @param fromNode
	 * @param toNode
	 * @param hlink
	 * @param tlink
	 */
	public Edge(){}	
	
	public Edge(Node fromNode, Node toNode, Edge hlink, Edge tlink){
		this.fromNode = fromNode;
		this.toNode = toNode;
		this.hlink = hlink;
		this.tlink = tlink; 
	}
	
	
	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}

	public Node GetFromNode(){
		return this.fromNode;
	}
	
	public Node GetToNode(){
		return this.toNode;
	}
	
	public Edge GetHLink(){
		return this.hlink;
	}
	
	public Edge GetTLink(){
		return this.tlink;
	}
	
	public void SetFromNode(Node fnode){
		this.fromNode = fnode;
	}
	
	public void SetToNode(Node tnode){
		this.toNode = tnode;
	}
	
	public void SetHLink(Edge hlink){
		this.hlink = hlink;
	}
	
	public void SetTLink(Edge tlink){
		this.tlink = tlink;
	}
	
	// 验证下equals方法的正确性
	public boolean equals(Object other){
		if(this == other)                                      //先检查是否其自反性，后比较other是否为空。这样效率高
			return true;
		if(other == null)         
			return false;
		if(!(other instanceof Edge))
			return false;

		final Edge e = (Edge) other;
		if(!this.fromNode.equals(e.GetFromNode()) || !this.toNode.equals(e.GetToNode())){
			return false;
		}
		return true;
	}
	
	public int hashcode(){
		int result = String.valueOf(this.fromNode).hashCode()+String.valueOf(this.toNode).hashCode();
		return result;
	}
}
