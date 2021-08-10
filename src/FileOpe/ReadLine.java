package FileOpe;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;

public class ReadLine {
	
//	private String encoding="UTF-8";
	private String encoding = "GBK";

	
	public void readLine(String path) throws IOException{
		
		BufferedReader reader = null;
		try
		{
//			reader = new BufferedReader(new FileReader(file));
			reader = new BufferedReader(new InputStreamReader(new FileInputStream(path), encoding));
			String text = null;
			while ((text = reader.readLine()) != null)
			{
				System.out.println(text);
			}
		} catch (FileNotFoundException e)
		{
			e.printStackTrace();
		}
	}

	public void readLineFromTXT(String path){
		try {
//			String encoding="GBK";
//			File file = new File(path);	//	if(file.isFile() && file.exists()){
//				InputStreamReader read = new InputStreamReader(
//						new FileInputStream(file),encoding);
//				BufferedReader bufferedReader = new BufferedReader(read);
//				String lineTxt = null;
//				while((lineTxt = bufferedReader.readLine()) != null){
//					System.out.println(lineTxt);
//				}
//				read.close();
			FileWriter fileWriter=new FileWriter("D:/Data/railstation/data/id_record_new.txt");
			BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(path)));
			int counter = 0; 
			for (String line = br.readLine(); line != null; line = br.readLine()) {
				if(counter == 17823136 || counter == 17823135){//17823136
					counter++;
					continue;
				}
				else{
					String[] array = line.split("	");
					String str = String.valueOf(counter);
					for(int i = 0; i< array.length ; i++){
						if(i!=6 && i!=7){
							str = str + "	" + array[i];
						}
						else if(i==6){
							if(array[6].trim().length() < 18){
								str = str + "	" + array[6].trim() + "	" + "*" + "	" + "*" ;
							}
							else if(array[6].trim().length() == 18){
								if(counter == 17823135){
									break;
								}
								String area = array[6].substring(0, 6);
								String yearmonth = array[6].substring(6, 12);
								int sex = Integer.valueOf(array[6].substring(16, 17)); 
								String xb = "";
								if(sex%2==0){
									xb = "female";
								}
								else if(sex%2==1){
									xb = "male";
								}
								str = str + "	" + area + "	" + yearmonth + "	" + xb;
							}
						}
					}
					System.out.println(str);
					fileWriter.write(str);
					fileWriter.write("\n");
					counter++;
				}
			}
			fileWriter.flush();
			fileWriter.close();
			br.close();
		} catch (Exception e) {
			System.out.println(e);
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) throws IOException{
//		String path = "D:/Data/gplus/gplus/imc12/google-2000.txt";
//		String path = "D:/Data/gplus/gplus/imc12/attri_type.txt";		

		String path = "D:/Data/railstation/id/id_no20150401.txt";
//		String path = "D:/Data/railstation/sales/sale_record20150401.bcp";
//		String path = "D:/Data/gplus/gplus/imc12/node_attri.txt";
		ReadLine rl = new ReadLine();
//		rl.readLineFromTXT(path);
		rl.readLine(path);
	}
}
