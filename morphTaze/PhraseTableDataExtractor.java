import java.util.*;
import java.io.*;
import java.util.zip.*;

public class PhraseTableDataExtractor {
	
	public static void main(String[] args) throws Exception{

		// lemma | features ||| in europe ||| 0.829007 0.207955 0.801493 0.492402 2.718
		String file = args[0];
		Scanner input = new Scanner(new GZIPInputStream(new FileInputStream(file)));
		HashMap<String, TreeSet<String>> prs_tbl = new HashMap<String, TreeSet<String>>();
		
		while(input.hasNextLine()) {

			String[] line = input.nextLine().split(" \\|\\|\\| ");
			if (line[0].trim().split(" ").length > 1)
				continue;
			String[] source = line[0].trim().split("\\|");
			String lemma = source[0];
			String features = source[1];
			String target = line[1];
			String[] scores = line[2].trim().split(" ");
			String key = lemma + " | " + target;

			/*if(lemma.indexOf(',') != -1)
				System.out.println(lemma);
			if(source.length > 2)
				System.out.printf("REPLACEMENT PROBLEM: %s\n", line[0]);*/

			TreeSet<String> set_of_featVecs = prs_tbl.containsKey(key) ? prs_tbl.get(key)
																	: new TreeSet<String>();
			set_of_featVecs.add(features);
			prs_tbl.put(key, set_of_featVecs);

		}

		int class_num = 0;
		HashMap<String, Integer> discrete_class_associations = new HashMap<String, Integer>();
		for(String key : prs_tbl.keySet()) {

			TreeSet<String> set_of_featVecs = prs_tbl.get(key);
			String lemma = key.split(" \\| ")[0]; 
			String _class = set_of_featVecs.toArray()[0].toString(); /*$%^&*/
			int disc_class = -1;

			if(discrete_class_associations.containsKey(_class))
				disc_class = discrete_class_associations.get(_class);
			else {
				discrete_class_associations.put(_class, class_num);
				disc_class = class_num++;
			}

			for(String featVec : set_of_featVecs) {
				System.out.printf("%s,%s,%d\n", lemma, featVec, disc_class);
			}

		}
		System.out.println("\n------------------------------\n");
		System.out.printf("NUMBER OF GROUPS: %d\nNUMBER OF CLASSES: %d\n", prs_tbl.keySet().size(), 
														discrete_class_associations.keySet().size());
		System.out.println("\n------------------------------\n");
		for(String key : discrete_class_associations.keySet())
			System.out.printf("%d ---> %s\n", discrete_class_associations.get(key), key);
	}

}