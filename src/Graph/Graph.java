package Graph;

import java.io.Serializable;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Random;
import java.util.Vector;

import FileOpe.WriteFile;

public class Graph implements Serializable{


	private static final long serialVersionUID = 145271638770783020L;
	/**
	 * @String id
	 * @Node node
	 */
	private HashMap<String, Node> NodeSet;						//	maintains the whole set of nodes in the Graph. 
	private HashSet<Edge> EdgeSet;								//	maintains the whole set of edges in the Graph.
	private HashSet<Node> NodeSets;                             //  存放点集合的；
	
	//用以寻找边类型的数据
	private HashMap< String, Edge > EdNoSet; 
	
	
	
	

	/**
	 * constructor
	 */
	public Graph(){
		this.NodeSet = new HashMap<String, Node>();
		this.EdgeSet = new HashSet<Edge>();
		this.EdNoSet = new HashMap< String, Edge >();
		this.NodeSets = new HashSet<Node>();
	}
	
	
	
	public HashSet<Node> getNodeSets() {
		return NodeSets;
	}



	public void setNodeSets(HashSet<Node> nodeSets) {
		NodeSets = nodeSets;
	}



	public HashMap<String, Node> GetNodeSet(){
		return this.NodeSet;
	}
	
	public int GetNodeSize(){
		return this.NodeSet.size();
	}
		
	public HashSet<Edge> GetEdgeSet(){
		return this.EdgeSet;
	}
	
	public int GetEdgeSize(){
		return this.EdgeSet.size();
	}
	
	public void SetNodeSet(HashMap<String, Node> NodeSet){
		this.NodeSet = NodeSet;
	}
	
	public HashMap<String, Edge> getEdNoSet() {
		return EdNoSet;
	}

	public void setEdNoSet(HashMap<String, Edge> edNoSet) {
		EdNoSet = edNoSet;
	}

	/**
	 * insert a new node in the graph.
	 * @param n
	 */
	public void InsNode(Node n){
		if(this.NodeSet != null && n != null){
			if(!this.NodeSet.values().contains(n)){
				this.NodeSet.put(n.GetID(), n);
				NodeSets.add(n);
			}	
		}
	}
	
	/**
	 * 
	 * @param n : label of the corresponding node
	 */
	public void InsNode(String id, String label){
         Node n = new Node(id, label, null, null);
		 this.InsNode(n);
	}
	
	/**
	 * delete a node and all the edges connecting to the node
	 * 删点操作等同于, 1) 删除所有与该点连接的边, 2) 然后再删除点.
	 * @param n
	 */
	public void DelNode(Node n){
		this.NodeSet.remove(n.GetID());	//  remove the node from node set. 
		this.NodeSets.remove(n);
		// 需要调整this.edgeSize
		// 1. process n's parents
		Edge ep = n.GetFirstIn();
		if(ep!=null){
			for(Edge e = ep; e!=null; e = e.GetHLink()){
				Node fv = e.GetFromNode();
				for(Edge e1 = fv.GetFirstOut(); e1!=null; e1 = e1.GetTLink()){
					Edge e2 = e1.GetTLink();				// e2.GetToNode() 有可能是n
					Node cfv = e1.GetToNode();
					if(cfv.equals(n)){							//	e1.firstout 指向了被删除的边
						fv.SetFirstOut(e2);						// 如果e1.tonode = n, 则设置fv的firstout为e2
						this.EdgeSet.remove(e1);			//	e1是删除的边
						break;
					}
					else{
						Node cfv2 = e2.GetToNode();
						if(cfv2.equals(n)){
							e1.SetTLink(e2.GetTLink());		//	e2 是 e1的邻边, 如果e2.tonode = n (说明e2为被删除的边), 则设置e1的tlink为e2的tlink
							this.EdgeSet.remove(e2);
							break;
						}
					}
				}
			}
		}

		// 2. process n's children
		ep = n.GetFirstOut();
		if(ep!=null){
			for(Edge e = ep; e!=null; e = e.GetTLink()){
				Node tv = e.GetToNode();
				for(Edge e1 = tv.GetFirstIn(); e1!=null; e1 = e1.GetHLink()){
					Edge e2 = e1.GetHLink();
					Node ptv= e1.GetFromNode();
					if(ptv.equals(n)){
						tv.SetFirstIn(e2);
						this.EdgeSet.remove(e1);
						break;
					}
					else{
						Node ptv2 = e2.GetFromNode();
						if(ptv2.equals(n)){
							e1.SetHLink(e2.GetHLink());
							this.EdgeSet.remove(e2);
							break;
						}
					}
				}				
			}
		}		
	}	
	
	public void InsEdge(Edge e){
		Node fv = e.GetFromNode();
		Node tv = e.GetToNode();
		String type = e.getType();
		if(type != null){
			this.InsEdge(fv, tv, type);
		}else{
			this.InsEdge(fv, tv, "");
		}
	}

	/**
	 * this procedure inserts a new edge into graph. 
	 * @param fv : from node
	 * @param tv : to node
	 */
//	public void InsEdge(Node fv, Node tv){
//		if(fv != null && tv !=null){
//			if(!this.ContainsEdge(fv, tv)){  //如果fv，tv之间不存在边的话
//				Edge e = new Edge();
//				if(fv.getType().equals("D")){  //director与movie之间的关系
//					e.setType("D");
//				}
//				else if(fv.getType().equals("A")){   //actor与movie之间的关系
//					//这里考虑设置边的类型既可能为A，也可能
//					if(this.GetNodeSet().containsKey(tv.GetID())){
//						//先删掉原来的旧边；
//						//System.out.println(tv !=null && fv !=null);
//						if(tv !=null && fv !=null){
//							this.DelEdge(fv, tv);
//					         e.setType("AD");
//						}
//					}else
//					e.setType("A");       
//				}
//				e.SetFromNode(fv);
//				e.SetToNode(tv);
//				Edge hlink = tv.GetFirstIn();
//				Edge tlink = fv.GetFirstOut();
//				e.SetHLink(hlink);
//				e.SetTLink(tlink);
//				fv.SetFirstOut(e);
//				tv.SetFirstIn(e);
//				this.EdgeSet.add(e); //这里还有边的集合
//			}	
//		}
//	}
	
	
	
	
//	//有边属性
//	public void InsEdge(Node fv, Node tv,String EdgeType){
//		if(fv != null && tv != null){
////			System.out.println(this.ContainsEdge(fv, tv));
//			if(!this.ContainsEdge(fv, tv)){
//				Edge e = new Edge();
//				String key = fv.GetID()+"&"+tv.GetID();
//				e.setType(EdgeType); //设置边的属性
//				e.SetFromNode(fv);
//				e.SetToNode(tv);
//				Edge hlink = tv.GetFirstIn();
//				Edge tlink = fv.GetFirstOut();
//				e.SetHLink(hlink);
//				e.SetTLink(tlink);
//				fv.SetFirstOut(e);
//				tv.SetFirstIn(e);
//				this.EdgeSet.add(e);
////				System.out.println("idKey: "+key+" Edge: "+e);
//				this.EdNoSet.put(key, e);
////				System.out.println("插入了边1");
//			}
//		}
//	}
//	
//	
	
	
	
	// 这里主要是用于判断边是关系还是属性
	public void InsEdge(Node fv, Node tv,String EdgeType){
		if(fv != null && tv != null){
			if(!this.ContainsEdge(fv, tv)){
				Edge e = new Edge();
				String key = fv.GetID()+"&"+tv.GetID();
				e.setType(EdgeType); //设置边的属性
				e.SetFromNode(fv);
				e.SetToNode(tv);
				Edge hlink = tv.GetFirstIn();
				Edge tlink = fv.GetFirstOut();
				e.SetHLink(hlink);
				e.SetTLink(tlink);
				fv.SetFirstOut(e);
				tv.SetFirstIn(e);
				this.EdgeSet.add(e);
//				System.out.println("idKey: "+key+" Edge: "+e);
				this.EdNoSet.put(key, e);
//				System.out.println("插入了边1");
			}
		}
	}
	
	
	
	
	//无边属性
	public void InsEdge(Node fv, Node tv){
		if(fv != null && tv != null){
			if(!this.ContainsEdge(fv, tv)){
				Edge e = new Edge();
				String key = fv.GetID()+"&"+tv.GetID();
//				e.setType(EdgeType); //设置边的属性
				e.SetFromNode(fv);
				e.SetToNode(tv);
				Edge hlink = tv.GetFirstIn();
				Edge tlink = fv.GetFirstOut();
				e.SetHLink(hlink);
				e.SetTLink(tlink);
				fv.SetFirstOut(e);
				tv.SetFirstIn(e);
				this.EdgeSet.add(e);
				this.EdNoSet.put(key, e);
//				System.out.println("插入了边2");
			}
		}
	}
	
	
	
	
	/**
	 * remove the specified edge 
	 * @param e
	 */
	public void DelEdge(Edge e){
		Node fv = e.GetFromNode();
		Node tv = e.GetToNode();
		this.DelEdge(fv, tv);
	}
	
	/**
	 * remove an edge with fv as tail node and tv as head node.
	 */
	public void DelEdge(Node fv, Node tv){
		// 需要调整this.edgeSize 
		// 修改fv的出弧链表
		Edge e1 = fv.GetFirstOut();
		if(fv != null && tv != null && e1 !=null){
			if(e1.GetToNode().equals(tv)){		// 如果fv的firstout边恰好是被删除的边
				fv.SetFirstOut(e1.GetTLink());	//	e1的tlink可能为null
				this.EdgeSet.remove(e1);
			
			}else{
			for(Edge e=e1; e!=null; e = e.GetTLink()){	//	遍历与e有相同tail node的边
				Edge ne = e.GetTLink();			//	ne 可能为null
				if(ne!=null){
					if(ne.GetToNode().equals(tv)){		//	ne 是即将删除的边, 那么需要将e.tlink调整为ne.tlink
						e.SetTLink(ne.GetTLink());
						this.EdgeSet.remove(ne);
						break;
					}
				}
			}
		}
	}
		
		//	修改tv的入弧链表
		e1 = tv.GetFirstIn();
//		System.out.print(e1 == null); 
//		System.out.println(" 判断e1是否为空");

		
			if(e1 != null && e1.GetFromNode().equals(fv)){		//	如果tv的firstin边恰好是被删除的边
				tv.SetFirstIn(e1.GetHLink());			//	e1.hlink可能为null
				this.EdgeSet.remove(e1);
			}else{
				for(Edge e=e1; e!=null; e = e.GetHLink()){
					Edge ne = e.GetHLink();		//	ne 可能为null
					if(ne!=null){
						if(ne.GetFromNode().equals(fv)){		//	ne 是即将删除的边，那么需要将e.hlink调整为ne.hlink
							e.SetHLink(ne.GetHLink());
							this.EdgeSet.remove(ne);
							break;
						}
					}
				}
			}
		
   }
	
	/**
	 * finds a node with the specified node id
	 * @param id
	 *该部分代码需要修改  id String
	 */
	public Node FindNode(int id){
		return this.NodeSet.get(id);
	}
	
	/**
	 * finds a node randomly
	 * @return
	 */
	public Node FindANode(){
		Vector<String> vec = new Vector<String>();
		for(String str : this.NodeSet.keySet()){
			vec.add(str);
		}
		int idx = (int) (Math.random()*this.NodeSet.size());
		System.out.println("vec.get(idx): "+vec.get(idx));
		System.out.println("this.NodeSet.get(vec.get(idx)).GetAttribute_str()  "+this.NodeSet.get(vec.get(idx)).GetAttribute_str());
		return this.NodeSet.get(vec.get(idx));
	}
	
	
	/**
	 * 保证随机选取节点的属性 not is *
	 * @return
	 */
	public Node FindANodeNotStart(){
		String attr="";
		
		int idx=0;
		Vector<String> vec = new Vector<String>();
		for(String str : this.NodeSet.keySet()){
			if(!this.NodeSet.get(str).GetAttribute_str().equals("*")){
				vec.add(str);
			}	
		}
		return this.NodeSet.get(vec.get(idx));
	}
	
	
	
	//得到两节点之间的边
	public Edge getEdge( Node fv, Node tv){
		Edge e = new Edge();
//		String key = fv.GetID() + tv.GetID();
		String key = fv.GetID()+"&"+tv.GetID();
		if(this.EdNoSet != null){
			e = this.EdNoSet.get(key);
		}
		return e;
	}
	
	
	
	/**
	 * this procedure checks whether the current graph contains the specified node
	 * @param v
	 * @return
	 */
	public boolean ContainsNode(Node v){
		if(this.NodeSet.values().contains(v)){
			return true;
		}
		return false;
	}
	
	/**
	 * this procedure checks whether the current graph contains the edge with two end nodes
	 * @param fv
	 * @param tv
	 * @return
	 */
	public boolean ContainsEdge(Node fv, Node tv){
		if(fv != null){
			Edge e1 = fv.GetFirstOut();
			for(Edge ee = e1; ee!=null; ee  = ee.GetHLink()){
				Node child = ee.GetToNode();
				if(child.equals(tv)){
					return true;
				}
			}
		}
		return false;
	}
	
	/**
	 * this procedure checks whether the current graph contains the specified edge
	 * @param e
	 * @return
	 */
	public boolean ContainsEdge(Edge e){
		Node fv = e.GetFromNode();
		Node tv = e.GetToNode();
		return this.ContainsEdge(fv, tv);
	}
	
	/**
	 * get children nodes of n
	 * @param n 
	 * @return
	 */
	public HashSet<Node> GetChildren(Node n){
		HashSet<Node> cSet = new HashSet<Node>();
		Queue<Edge> q = new LinkedList<Edge>();
		Edge e = n.GetFirstOut();
		if(e!=null){
			q.add(e);
		}
		while(!q.isEmpty()){
			Edge ee = q.poll();
			cSet.add(ee.GetToNode());
			Edge ne = ee.GetTLink();
			if(ne!=null){
				q.add(ne);
			}
		}
		return cSet;
	}
	
	
	/**
	 * get parent nodes of n
	 * @param n
	 * @return
	 */
	public HashSet<Node> GetParents(Node n){
		HashSet<Node> pSet = new HashSet<Node>();
		Edge e1 = n.GetFirstIn();
		for(Edge e = e1; e!=null; e  = e.GetHLink()){
			Node parent = e.GetFromNode();
			pSet.add(parent);
		}
		return pSet;
	}
	
	public void BFS(Node n){
		HashSet<Node> visited = new HashSet<Node>();
		Queue<Node> queue = new LinkedList<Node>();
		visited.add(n);
		queue.add(n);
		while(!queue.isEmpty()){
			Node sn = queue.poll();
			Edge e1 = sn.GetFirstOut();
			for(Edge e = e1; e!=null; e  = e.GetTLink()){
				Node child = e.GetToNode();
				if(!visited.contains(child)){
					visited.add(child);
					queue.add(child);
				}
			}
		}
	}
	
	
	/**
	 * this procedure generates k-hop subgraph starting from the specified node
	 * @param n
	 * @param d
	 */
	public SubGraph Gen_d_Hop_Induced_SubGraph(Node n, int d){
		SubGraph sub = new SubGraph();
		HashMap<Node, Integer> visited = new HashMap<Node, Integer>();
		Queue<Node> queue = new LinkedList<Node>();
		int dis = 0;
		visited.put(n, dis);
		sub.InsNode(n);
		while(!queue.isEmpty()){
			Node sn = queue.poll();
			dis = visited.get(sn);
			Edge e1 = sn.GetFirstOut();
			for(Edge e = e1; e!=null; e  = e.GetTLink()){
				Node child = e.GetToNode();
				if(!visited.keySet().contains(child)){
					dis = dis + 1;
					if(dis<=d){
						visited.put(child, dis);
						queue.add(child);
						sub.InsNode(child);
						sub.InsEdge(sn, child,"");
					}
				}
				else if(visited.keySet().contains(child)){
					sub.InsEdge(sn, child,"");
				}
			}
		}
		return sub;
	}
	
	/**
	 * displays graph structure using adjacency list. 
	 */
	public void Display(){
		System.out.println("The graph has the following structure: ");
		for(String nid : this.NodeSet.keySet()){
			Node n = this.NodeSet.get(nid);
			Edge e1 = n.GetFirstOut();
			String s = "";
			if(e1!=null){
				for(Edge e = e1; e != null; e = e.GetTLink()){
					
					s = s + "\t" + e.GetToNode().GetID() + "\t"+"\t" + e.getType();
				}
				if(!s.equals(""))
					s = s.substring(1);
			}
			//System.out.println(n.GetID() + "\t" + n.GetAttribute_str()  + "\t|\t" + n.GetAttribute_short() + "\t" + s);
			System.out.println(n.GetID() + "\t" + n.GetAttribute_str()  + "\t|\t" + s);
		}		
	}
	
	/**
	 * this procedure generates the induced subgraph with the specified node set
	 * @param vset
	 * @return
	 */
	public SubGraph GenInducedSubGraph(Collection<Node> vset){
		SubGraph subG = new SubGraph();

		for(Node n : vset){
			subG.InsNode(n);
		}
		int i = 0;
		for(Node fv : subG.GetNodeSet().values()){
			for(Node tv : subG.GetNodeSet().values()){
				System.out.println(fv.GetID() + "->" + tv.GetID() + ": " +  this.ContainsEdge(fv, tv) + ", " + subG.ContainsEdge(fv, tv));
				if(this.ContainsEdge(fv, tv) && !subG.ContainsEdge(fv, tv)){
					subG.InsEdge(fv, tv,"");
					i++;
					System.out.println(i + "edges are inserted");
				}
			}
		}
		return subG;
	}
	
	// test how large a graph can be loaded by using Orthogonal list. 
	public void Init(){
		for(int i = 0; i<4; i++){
			Node n = new Node(String.valueOf(i));
			this.InsNode(n);
		}
		Node n0 = this.FindNode(0);
		Node n1 = this.FindNode(1);
		Node n2 = this.FindNode(2);
		Node n3 = this.FindNode(3);
		
		this.InsEdge(n0, n1,"");
		this.InsEdge(n0, n2,"");
		this.InsEdge(n0, n3,"");
		this.InsEdge(n1, n2,"");
		this.InsEdge(n3, n2,"");
	}
	
	public Graph RanGraphGen(int vsize, int esize){
		// initialise node label set
//		String str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
//		char[] lset = str.toCharArray();
		short[] attrSet = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26};
		Random random = new Random();
		
		// add nodes
		for(int i = 0; i < vsize; i++){
			short label = attrSet[random.nextInt(26)];
			Node n = new Node(String.valueOf(i), String.valueOf(label), null, null);
			this.NodeSet.put(n.GetID(), n);
			this.NodeSets.add(n);
		}
		// add edges
		for(int i = 0; i<esize; i++){
			Node fn = this.NodeSet.get((int)(Math.random()*vsize));
			Node tn = this.NodeSet.get((int)(Math.random()*vsize));
			while(fn.equals(tn) || this.ContainsEdge(fn, tn)){
				fn = this.NodeSet.get((int)(Math.random()*vsize));
				tn = this.NodeSet.get((int)(Math.random()*vsize));
			}
			Edge e = new Edge();
			e.SetFromNode(fn);
			e.SetToNode(tn);
			Edge hlink = tn.GetFirstIn();
			Edge tlink = fn.GetFirstOut();
			e.SetHLink(hlink);
			e.SetTLink(tlink);
			fn.SetFirstOut(e);
			tn.SetFirstIn(e);
			this.EdgeSet.add(e);
		}
		return this;
	}
	
	
	public static void main(String[] args){
		Graph G = new Graph();
		G.RanGraphGen(1000, 2000);
		G.Display();
//		WriteFile wf = new WriteFile();
//		wf.WriteGraph("D://Data//Random//G", G);
/**
    	G.NodeSet = new LinkedList<Node>();
		G.RanGraphGen(1000000, 5000000);
		
		for(Node n : G.NodeSet){
			HashSet<Node> cSet = G.GetChildren(n);
			String cStr = "";
			for(Node c : cSet){
				cStr = cStr + ", " +String.valueOf(c.GetID());
			}
			if(!cStr.equals("")){
				cStr = cStr.substring(1);
			}
			System.out.println(n.GetID() + "    " +cStr);
		}
*/
	}
	
}
