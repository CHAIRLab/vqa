package FileOpe;

import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;

import Graph.Graph;
import Graph.SubGraph;

public class WriteFile {
	
	public void writeobject(String filePath, Object o){
		double start3;
		double end3;
		start3 = System.currentTimeMillis();
		try{
			FileOutputStream fos = new FileOutputStream(filePath, true);
			BufferedOutputStream bos = new BufferedOutputStream(fos);
			ObjectOutputStream oos = new ObjectOutputStream(bos);
			oos.writeObject(o);
			oos.close();
		}catch(IOException ee){
			System.err.println("IOError" + ee.getMessage());
		}catch (Exception e){//Catch exception if any
			System.err.println("Error: " + e.getMessage());
		}
		end3 = System.currentTimeMillis();
		System.out.println("storage time:"+ (end3-start3));
	}
	
	
	public void WriteGraph(String filePath, Graph g){
		double start3;
		double end3;
		start3 = System.currentTimeMillis();
		try{
			FileOutputStream fos = new FileOutputStream(filePath, true);
			BufferedOutputStream bos = new BufferedOutputStream(fos);
			ObjectOutputStream oos = new ObjectOutputStream(bos);
			oos.writeObject(g);
			oos.close();
		}catch(IOException ee){
			System.err.println("IOError" + ee.getMessage());
		}catch (Exception e){//Catch exception if any
			System.err.println("Error: " + e.getMessage());
		}
		end3 = System.currentTimeMillis();
		System.out.println("storage time:"+ (end3-start3));
	}
	
	public void WriteSubGraph(String filePath, SubGraph o){
		double start3;
		double end3;
		start3 = System.currentTimeMillis();
		try{
			FileOutputStream fos = new FileOutputStream(filePath, true);
			BufferedOutputStream bos = new BufferedOutputStream(fos);
			ObjectOutputStream oos = new ObjectOutputStream(bos);
			oos.writeObject(o);
			oos.close();
		}catch(IOException ee){
			System.err.println("IOError" + ee.getMessage());
		}catch (Exception e){//Catch exception if any
			System.err.println("Error: " + e.getMessage());
		}
		end3 = System.currentTimeMillis();
		System.out.println("storage time:"+ (end3-start3));
	}
}
