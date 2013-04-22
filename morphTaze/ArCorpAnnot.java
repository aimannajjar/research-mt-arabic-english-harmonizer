
import java.util.*;
import java.io.*;

public class ArCorpAnnot{
	
	public static void main(String[] args) throws Exception {
		
		String arCorp = args[0], factored_form = "", surf_form = "";
		Scanner input = new Scanner(new File(arCorp));

		while(input.hasNextLine()) {

			String line = input.nextLine();

			if(isSent(line) && factored_form.length() != 0) {

				System.out.println(factored_form.substring(0, factored_form.length() - 1));
				factored_form = "";
				continue;

			} if(isWord(line)) {

				surf_form = line.split(" ")[1].replaceAll("\\|", "P");
				continue;

			} if(isVec(line)) {

				String[] anal_vec = line.split(" ");
				String lemma = anal_vec[2].substring(anal_vec[2].indexOf(':') + 1);
				String feat_vec = extract_feats(anal_vec);
				factored_form += surf_form + "|" + lemma.replaceAll("\\|", "P")
												+ "|" + feat_vec + " ";
				continue;

			} if(noAnal(line)) {

				factored_form += surf_form + "|" + surf_form + "|-1,-1,-1,-1,-1,-1,-1,-1,-1,-1 ";
				continue;
			}
		}
		System.out.println(factored_form.substring(0, factored_form.length() - 1));
	}

	public static boolean isVec(String line) { return line.startsWith("*"); }
	public static boolean noAnal(String line) { return line.startsWith(";;NO-ANALYSIS"); }
	public static boolean isWord(String line) { return line.startsWith(";;WORD"); }
	public static boolean isSent(String line) { return line.startsWith(";;; SENTENCE"); }

	public static String extract_feats(String[] anal_vec) {
		//5, 10-17, 19
		String feat_vec = "", feat_val;
		int pos_idx = 5, rat_idx = 19, col_idx = -1;

		col_idx = anal_vec[pos_idx].indexOf(':');
		feat_val = anal_vec[pos_idx].substring(col_idx + 1);
		feat_vec += feat_val + ",";
		for (int i = 10 ; i < 18 ; i++) {
			col_idx = anal_vec[i].indexOf(':');
			feat_val = anal_vec[i].substring(col_idx + 1);
			feat_vec += feat_val.equals("na") ? "-1,"
							: "" + (int)feat_val.charAt(0) + ",";
		}
		col_idx = anal_vec[rat_idx].indexOf(':');
		feat_val = anal_vec[rat_idx].substring(col_idx + 1);
		feat_vec += feat_val.equals("na") ? "-1"
						: "" + (int)feat_val.charAt(0);
		return feat_vec;
	}
}