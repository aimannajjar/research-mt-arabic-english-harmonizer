import java.util.*;
import weka.classifiers.*;
import weka.core.*;
import java.io.*;
import weka.core.converters.*;

public class Driver {
	
	
	public static void main(String[] args) throws Exception{
		
		Scanner config = new Scanner(new File("Driver.config"));
		
		String csv_trainFile = config.nextLine();
		String attr_file = config.nextLine();
		String LEMMA_FEATURE_TREATMENT = config.nextLine();
		int num_examples = Integer.parseInt(config.nextLine());
		
		System.out.println(csv_trainFile);
		System.out.println(attr_file);
		System.out.println(LEMMA_FEATURE_TREATMENT);
		System.out.println(num_examples);
		
		ArrayList<Attribute> attributes = new ArrayList<Attribute>();
		init_attributes(attr_file, attributes);
		Instances data = new Instances(csv_trainFile, attributes, num_examples);
		data.setClassIndex(attributes.size() - 1);
		
		
		if(LEMMA_FEATURE_TREATMENT.equalsIgnoreCase("NONE")) {
			Scanner input = new Scanner(new File(csv_trainFile));
			while(input.hasNextLine()) {
				String tmp_line = input.nextLine();
				System.out.println(tmp_line.substring(tmp_line.indexOf(',') + 1));
				String[] line = tmp_line.substring(tmp_line.indexOf(',') + 1).split(",");
				if(line.length < 2)
					break;
				int i = 0;
				Instance example = new DenseInstance(line.length);
				for(String val : line) {
					/*System.out.println(val);
					System.out.println(attributes.get(i));*/
					example.setValue(attributes.get(i++), val);
				}
				data.add(example);
			}
			ArffSaver saver = new ArffSaver();
			saver.setInstances(data);
			saver.setFile(new File(csv_trainFile + ".arff"));
			saver.setDestination(new File(csv_trainFile + ".arff"));
			saver.writeBatch();
		}
		System.out.println("DONE");
		
	}
	public static void init_attributes(String file, ArrayList<Attribute> attributes) throws Exception {
		/* "Person -> {0,1,2,3}" */
		Scanner input = new Scanner(new File(file));
		while(input.hasNextLine()) {
			
			String[] line = input.nextLine().split(" -> ");
			String attr_name = line[0];
			ArrayList<String> values = new ArrayList<String>();
			int tmp_idx = line[1].indexOf('-');
			if(tmp_idx != -1){
				int start = Integer.parseInt(line[1].substring(0, tmp_idx));
				int end = Integer.parseInt(line[1].substring(tmp_idx + 1));
				for(int i = start; i <= end ; i++)
					values.add("" + i);
			} else {
				String[] vals = line[1].substring(1, line[1].length() - 1).split(",");
				Collections.addAll(values, vals);
			}
			attributes.add(new Attribute(attr_name, values));
		}
		
	}
}