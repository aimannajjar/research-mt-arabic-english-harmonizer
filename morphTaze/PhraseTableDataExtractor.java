import java.util.*;
import java.io.*;
import java.util.zip.*;

public class PhraseTableDataExtractor {

	static HashMap<String, Integer> pos_tbl = new HashMap<String, Integer>();

	public static void main(String[] args) throws Exception{
		init_pos_tbl();
		// lemma | features ||| in europe ||| 0.829007 0.207955 0.801493 0.492402 2.718
		String prs_tbl_file = args[0];
		String outTrainFile = args[1];
		String outClassMappingsFile = args[2];
		String dataAttributesInfoFile = args[3];
		Scanner input = new Scanner(new GZIPInputStream(new FileInputStream(prs_tbl_file)));
		HashMap<String, TreeSet<String>> prs_tbl = new HashMap<String, TreeSet<String>>();
		FileWriter fw1 = new FileWriter(outTrainFile);
		FileWriter fw2 = new FileWriter(outClassMappingsFile);
		FileWriter fw3 = new FileWriter(dataAttributesInfoFile);
		
		while(input.hasNextLine()) {

			String[] line = input.nextLine().split(" \\|\\|\\| ");
			if (line[0].trim().split(" ").length > 1)
				continue;
			String[] source = line[0].trim().split("\\|");
			String lemma = source[0];
			String features = source[1].replaceAll("-1", "0");
			if(no_good(features))
				continue;
			String target = line[1];
			String[] scores = line[2].trim().split(" ");
			String key = lemma + " | " + target;

			TreeSet<String> set_of_featVecs = prs_tbl.containsKey(key) ?
													prs_tbl.get(key) :
													new TreeSet<String>();
			set_of_featVecs.add(features);
			prs_tbl.put(key, set_of_featVecs);

		}
		int class_num = 0;
		HashMap<String, Integer> discrete_class_associations = new HashMap<String, Integer>();
		for(String key : prs_tbl.keySet()) {

			TreeSet<String> set_of_featVecs = prs_tbl.get(key);
			String lemma = key.split(" \\| ")[0].replaceAll(",", " ");/*$%^&*/ 
			String _class = set_of_featVecs.toArray()[0].toString();
			int disc_class = -1;

			if(discrete_class_associations.containsKey(_class))
				disc_class = discrete_class_associations.get(_class);
			else {
				discrete_class_associations.put(_class, class_num);
				disc_class = class_num++;
			}

			for(String featVec : set_of_featVecs) {
				String pos = featVec.substring(0, featVec.indexOf(','));
				String normalized_featVec = featVec.replaceAll(pos, "" + pos_tbl.get(pos));
				String sample = lemma + "," + normalized_featVec + "," + disc_class;
				fw1.write(sample);
				fw1.write("\n");
				/*System.out.printf("%s,%s,%d\n", lemma, featVec, disc_class);*/
			}

		}
		/*System.out.println("\n------------------------------\n");*/
		System.out.printf("NUMBER OF GROUPS: %d\nNUMBER OF CLASSES: %d\n", prs_tbl.keySet().size(), 
									discrete_class_associations.keySet().size());
		/*System.out.println("\n------------------------------\n");*/
		for(String key : discrete_class_associations.keySet()){
			String association = discrete_class_associations.get(key) + " ---> " + key;
			fw2.write(association);
			fw2.write("\n");
		}
		
		writeDataInfo(fw3, discrete_class_associations.keySet().size());

		fw1.close();
		fw2.close();
	}
	public static boolean no_good(String str) {

		for(int i = 0 ; i < str.length() ; i++)
			if(str.charAt(i) != '0')
				return false;
		return true;

	}
	public static void writeDataInfo(FileWriter fw, int num_classes) throws Exception {

		/*
		Person: [1,2,3,na] # 1 = First, 2 = Second, 3 = Third, na = N/A
          Aspect: [c,i,p,na] # c = Command, i = Imperfective, p = Perfective, na = N/A
          Voice : [a,p,na,u] # a = Active, p = Passive, na = N/A, u = Undefined
          Mood  : [i,j,s,na,u] # i = Indicative, j = Jussive, s = Subjunctive, na = N/A 
          Gender: [f,m,na] # f = Feminine, m = Masculine, na = N/A
          Number: [s,p,d,na,u] # s = Singular, p = Plural, d = Dual, na = N/A, u = Undefined 
          State : [i,d,c,na,u] # i = Indefinite, d = Definite, c = Construct/Poss/Idafa, na = N/A, u = Undefined 
          Case  : [n,a,g,na,u] # n = Nominative, a = Accusative, g = Genitive, na = N/A, u = Undefined
          Rat** : [y,na] # y = yes, n = N/A*/
        fw.write("Pos -> 0-33" + "\n");
    	fw.write("Person -> {0,49,50,51}" + "\n");
    	fw.write("Aspect -> {99,105,112,0}" + "\n");
    	fw.write("Voice -> {97,112,0,117}" + "\n");
    	fw.write("Mood -> {105,106,115,0,117}" + "\n");
    	fw.write("Gender -> {102,109,0}" + "\n");
    	fw.write("Number -> {115,112,100,0,117}" + "\n");
    	fw.write("State -> {105,100,99,0,117}" + "\n");
    	fw.write("Case -> {110,97,103,0,117}" + "\n");
    	fw.write("Rat -> {121,0}" + "\n");
    	fw.write("class -> 0-" + (num_classes - 1));
    	fw.close();


	}
	public static void init_pos_tbl() {

		pos_tbl.put("noun", 0);
		pos_tbl.put("noun_num", 1);
		pos_tbl.put("noun_quant", 2);
		pos_tbl.put("noun_prop", 3);
		pos_tbl.put("adj", 4);
		pos_tbl.put("adj_comp", 5);
		pos_tbl.put("adj_num", 6);
		pos_tbl.put("adv", 7);
		pos_tbl.put("adv_interrog", 8);
		pos_tbl.put("adv_rel", 9);
		pos_tbl.put("pron", 10);
		pos_tbl.put("pron_dem", 11);
		pos_tbl.put("pron_exclam", 12);
		pos_tbl.put("pron_interrog", 13);
		pos_tbl.put("pron_rel", 14);
		pos_tbl.put("verb", 15);
		pos_tbl.put("verb_pseudo", 16);
		pos_tbl.put("part", 17);
		pos_tbl.put("part_det", 18);
		pos_tbl.put("part_focus", 19);
		pos_tbl.put("part_fut", 20);
		pos_tbl.put("part_interrog", 21);
		pos_tbl.put("part_neg", 22);
		pos_tbl.put("part_restrict", 23);
		pos_tbl.put("part_verb", 24);
		pos_tbl.put("part_voc", 25);
		pos_tbl.put("prep", 26);
		pos_tbl.put("abbrev", 27);
		pos_tbl.put("punc", 28);
		pos_tbl.put("conj", 29);
		pos_tbl.put("conj_sub", 30);
		pos_tbl.put("interj", 31);
		pos_tbl.put("digit", 32);
		pos_tbl.put("latin", 33);

	}

}