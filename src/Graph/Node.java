package Graph;

import java.io.Serializable;


public class Node implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = 5131093457054575909L;

	private String id;			//	node ID ��ʼ��
	private String attribute_str;		//	attribute of the node
	private String type;            //tag
	//private short attribute_short;		//	attribute of the node
	private Edge firstin;			//	first in node
	private Edge firstout;			//	first out node
	
	public Node(String id){
		this.id = id;
	}	
	

/*	public Node(String id, short attribute, Edge firstin, Edge firstout){
		this.id = id;
		this.attribute_short = attribute;
		this.firstin = firstin;
		this.firstout = firstout;
	}*/
	
	//���캯����String����
	public Node(String id, String attribute, Edge firstin, Edge firstout){
		this.id = id;
		this.attribute_str = attribute;
		this.firstin = firstin;
		this.firstout = firstout;
	}
	
	//���캯����String���� ; tag����
	public Node(String id, String attribute, String type, Edge firstin, Edge firstout){
		this.id = id;
		this.attribute_str = attribute;
		this.type = type;
		this.firstin = firstin;
		this.firstout = firstout;
	}
	
	
	public String GetID(){
		return this.id;
	}
	
/*	public short GetAttribute_short(){
		return this.attribute_short;
	}*/
	
	public String GetAttribute_str(){
		return this.attribute_str;
	}
	
	public Edge GetFirstIn(){
		return this.firstin;
	}
	
	public Edge GetFirstOut(){
		return this.firstout;
	}
	
	public String getType() {
		return this.type;
	}


	public void setType(String type) {
		this.type = type;
	}


	public void SetID(String ID){
		this.id = ID;
	}
	
	/*public void SetAttribute_short(short attribute){
		this.attribute_short = attribute;
	}*/
	
	public void SetAttribute_str(String attribute){
		this.attribute_str = attribute;
	}
	
	public void SetFirstIn(Edge firstin){
		this.firstin = firstin;
	}
	
	public void SetFirstOut(Edge firstout){
		this.firstout = firstout;
	}
	
	// ��֤��equals��������ȷ��
	public boolean equals(Object other){
		if(this == other)                                      //�ȼ���Ƿ����Է��ԣ���Ƚ�other�Ƿ�Ϊ�ա�����Ч�ʸ�
			return true;
		if(other == null)         
			return false;
		if(!(other instanceof Node))
			return false;

		final Node v = (Node) other;
		if(this.GetID()!=v.GetID()){
			return false;
		}
//		if(!this.GetAttribute().equals(v.GetAttribute())){
//			return false;
//		}
		return true;
	}
	
	public int hashCode(){                 //hashCode��Ҫ���������hashϵͳ�Ĳ�ѯЧ�ʡ���hashCode�в������κβ���ʱ������ֱ�����䷵�� һ���������߲�������д��
		int result = String.valueOf(this.GetID()).hashCode();
//		result = 29 * result +this.GetAttribute().hashCode();
		result = 29 * result;
		return result;
	}

}
