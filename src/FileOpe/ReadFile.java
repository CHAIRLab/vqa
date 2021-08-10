package FileOpe;

import java.io.*;
import org.json.*;

import Graph.Edge;
import Graph.Graph;
import Graph.Node;

public class ReadFile {
	
	
	//从scene graph中构建graph
	public Graph readJsonFromSG(String filePath) throws FileNotFoundException, UnsupportedEncodingException, JSONException {
		Graph p = new Graph();
		InputStream inputStream = new FileInputStream(filePath); 
		BufferedReader reader=new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
		JSONObject object7=new JSONObject(new JSONTokener(reader));
		JSONArray object8=object7.getJSONArray("triplet_trans");
		for(int i=0; i<object8.length(); i++) {
			JSONArray triplet = object8.getJSONArray(i);
			//构造三元组
			String subject = triplet.getString(0);
			String rel = triplet.getString(1);
			String object = triplet.getString(2);
//			System.out.println('('+subject.split("-")[0]+'\t'+rel+'\t'+object+")");
			Node sub = null;
			Node obj = null;
			Edge ee = new Edge();
			if(p.GetNodeSet().get(subject)!=null) {
				//graph中已存在节点
				sub = p.GetNodeSet().get(subject);
			}else {
				sub = new Node(subject, subject.split("-")[0], null, null);
				p.InsNode(sub);
			}
			if(p.GetNodeSet().get(object)!=null) {
				//graph中已存在节点
				obj = p.GetNodeSet().get(object);
			}else {
				obj = new Node(object, object.split("-")[0], null, null);
				p.InsNode(obj);
			}
			ee.SetFromNode(sub);
			ee.SetToNode(obj);
			ee.setType(rel);
			p.InsEdge(ee);
		}
		JSONArray object9=object7.getJSONArray("attribute_triplet");
		for(int i=0; i<object9.length(); i++) {
			JSONArray triplet = object9.getJSONArray(i);
			//构造三元组
			String subject = triplet.getString(0);
			String rel = triplet.getString(1);
			String object = triplet.getString(2);
//			System.out.println('('+subject.split("-")[0]+'\t'+rel+'\t'+object+")");
			Node sub = null;
			Node obj = null;
			Edge ee = new Edge();
			if(p.GetNodeSet().get(subject)!=null) {
				//graph中已存在节点
				sub = p.GetNodeSet().get(subject);
			}else {
				sub = new Node(subject, subject.split("-")[0], null, null);
				p.InsNode(sub);
			}
			obj = new Node(object+"-"+i, object, null, null); //属性值都不一样
			p.InsNode(obj);
			ee.SetFromNode(sub);
			ee.SetToNode(obj);
			ee.setType(rel);
			p.InsEdge(ee);
		}
//		p.Display();
		return p;
	}
	
	// 从word graph中构建graph
	public Graph readJsonFromWG(String filePath) throws FileNotFoundException, UnsupportedEncodingException, JSONException {
		Graph p = new Graph();
		InputStream inputStream = new FileInputStream(filePath); 
		BufferedReader reader=new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
		JSONArray object7 = new JSONArray(new JSONTokener(reader));
		for(int i=0; i<object7.length(); i++) {
			JSONArray object8 = object7.getJSONArray(i);
			Node sub = null;
			Node obj = null;
			Edge ee = new Edge();
			String subject = null;
			String object = null;
		    String rel = null;
			if(object8.length()==0) {
				continue;
			}else {
//				System.out.println(object8.getString(0)+'\t'+
//						object8.getString(1)+"\t"+object8.getString(2));
				if(object8.getString(0).equals("what")) {
					subject = object8.getString(2);
					object = "*";
				}else {
					subject = object8.getString(0);
					object = object8.getString(2);
				}
				rel = object8.getString(1);
			}
			if(p.GetNodeSet().get(subject)!=null) {
				//graph中已存在节点
				sub = p.GetNodeSet().get(subject);
			}else {
				sub = new Node(subject, subject, null, null);
				p.InsNode(sub);
			}
			if(p.GetNodeSet().get(object)!=null) {
				//graph中已存在节点
				obj = p.GetNodeSet().get(object);
			}else {
				obj = new Node(object, object, null, null);
				p.InsNode(obj);
			}
			ee.SetFromNode(sub);
			ee.SetToNode(obj);
			ee.setType(rel);
			p.InsEdge(ee);
		}
		return p;
		
		
		
//		JSONArray object8=object7.getJSONArray("triplet_trans");
//		for(int i=0; i<object8.length(); i++) {
//			JSONArray triplet = object8.getJSONArray(i);
//			//构造三元组
//			String subject = triplet.getString(0);
//			String rel = triplet.getString(1);
//			String object = triplet.getString(2);
////			System.out.println('('+subject.split("-")[0]+'\t'+rel+'\t'+object+")");
//			Node sub = null;
//			Node obj = null;
//			Edge ee = new Edge();
//			if(p.GetNodeSet().get(subject)!=null) {
//				//graph中已存在节点
//				sub = p.GetNodeSet().get(subject);
//			}else {
//				sub = new Node(subject, subject.split("-")[0], null, null);
//			}
//			if(p.GetNodeSet().get(object)!=null) {
//				//graph中已存在节点
//				obj = p.GetNodeSet().get(object);
//			}else {
//				obj = new Node(object, object.split("-")[0], null, null);
//			}
//			p.InsNode(sub);
//			p.ContainsNode(obj);
//			ee.SetFromNode(sub);
//			ee.SetToNode(obj);
//			ee.setType(rel);
//			p.InsEdge(ee);
//		}
//		p.Display();
//		return p;
	}
	
	
	
	
	
	public Object read(String filePath){		
		Object o = new Object();
		try{
			FileInputStream fis = new FileInputStream(filePath);
			BufferedInputStream bis = new BufferedInputStream(fis);
			ObjectInputStream ois = new ObjectInputStream(bis);
			o = ois.readObject();
			ois.close();			
		}catch (Exception e){//Catch exception if any
			System.err.println("Error: " + e.getMessage());
		}	
		return o;		
	}
	
	
	public Graph ReadGraph(String filePath){		
		Graph o = null;
		try{
			FileInputStream fis = new FileInputStream(filePath);
			BufferedInputStream bis = new BufferedInputStream(fis);
			ObjectInputStream ois = new ObjectInputStream(bis);
			o = (Graph) ois.readObject();
			ois.close();			
		}catch (Exception e){//Catch exception if any
			System.err.println("Error: " + e.getMessage());
		}	
		return o;		
	}
	
	public static void main(String args[]) throws FileNotFoundException, UnsupportedEncodingException, JSONException {
		
		System.out.println(System.getProperty("user.dir")); //当前路径地址
		ReadFile rf = new ReadFile();
		Graph g = rf.readJsonFromSG("src//Data//scene_graph//131091.json");
		g.Display();
	}
}
