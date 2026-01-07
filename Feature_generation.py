
import os

def feature_generation(ESTIMATE_score_result,meta_gene_relation_file,metabolite_expression_file,gene_expression_file):
    dict_estimate_id_value = {}
    fr00 = open(ESTIMATE_score_result,"r")
    dict_id = {}
    for line in fr00.readlines():
        sp = line.strip().split("\t")
        if len(sp) <= 2:
            continue
        else:
            if line.startswith("NAME\t"):
                for i in range(len(sp))[2:]:
                    id = sp[i].replace(".", "-")
                    dict_id[i] = id
            else:
                item = sp[0]
                for i in range(len(sp))[2:]:
                    id = dict_id[i]
                    value = sp[i]
                    putDictInDict(dict_estimate_id_value,item,id,value)

    dict_meta_id_inten, list_meta, list_id_meta = readMatrix_withZero(metabolite_expression_file, 1)
    dict_rna_id_inten, list_rna, list_id_rna = readMatrix_withZero(gene_expression_file, 1)
    fr0 = open(meta_gene_relation_file,"r")
    output_folder = "~/feature/"
    os.makedirs(output_folder, exist_ok=True)
    for line in fr0.readlines():
        if line.startswith("metabolite"):
            continue
        else:
            sp = line.strip().split("\t")
            meta = sp[0]
            if len(dict_meta_id_inten[meta]) < 10 or all_values_zero(dict_meta_id_inten[meta]):
                print(meta)
                # continue
            else:
                fw = open("~/feature/" + meta + ".tsv","w")
                list_id = []
                dict_id_inten_meta = dict_meta_id_inten[meta]
                for id in dict_id_inten_meta:
                    list_id.append(id)
                list_feature = []
                dict_feature_intens = {}
                #microenviroment
                list_feature.append("StromalScore_mic")
                dict_feature_intens["StromalScore_mic"] = dict_estimate_id_value["StromalScore"]
                list_feature.append("ImmuneScore_mic")
                dict_feature_intens["ImmuneScore_mic"] = dict_estimate_id_value["ImmuneScore"]
                list_feature.append("ESTIMATEScore_mic")
                dict_feature_intens["ESTIMATEScore_mic"] = dict_estimate_id_value["ESTIMATEScore"]
                list_feature.append("TumorPurity_mic")
                dict_feature_intens["TumorPurity_mic"] = dict_estimate_id_value["TumorPurity"]
                # enzyme
                for index in range(2, 5):
                    if len(sp) > index and sp[index] != "":
                        sp_enzyme = sp[index].split("@")
                        for i in range(len(sp_enzyme)):
                            enzyme = sp_enzyme[i]
                            if enzyme in dict_rna_id_inten and is_half_coverd(dict_id_inten_meta,
                                                                              dict_rna_id_inten[enzyme]):
                                list_feature.append(enzyme + "_RNA")
                                dict_feature_intens[enzyme + "_RNA"] = dict_rna_id_inten[enzyme]
                if len(sp) >= 6:
                    sp5 = sp[5].split("@")
                    for i in range(len(sp5)):
                        up_meta = sp5[i]
                        if up_meta in dict_meta_id_inten and is_half_coverd(dict_id_inten_meta,
                                                                            dict_meta_id_inten[up_meta]):
                            list_feature.append(up_meta + "_upmeta")
                            dict_feature_intens[up_meta + "_upmeta"] = dict_meta_id_inten[up_meta]
                fw.write("ID")
                for i in range(len(list_feature)):
                    feature = list_feature[i]
                    fw.write("\t" + feature)
                fw.write("\tmeta\n")

                for a in range(len(list_id)):
                    id = list_id[a]
                    if id != "":
                        fw.write(id)
                        for i in range(len(list_feature)):
                            feature = list_feature[i]
                            dict_id_inten = dict_feature_intens[feature]
                            if id in dict_id_inten:
                                fw.write("\t" + str(dict_id_inten[id]))
                            else:
                                fw.write("\t" + "NA")
                        fw.write("\t" + dict_id_inten_meta[id])
                        fw.write("\n")

                fw.flush()
                fw.close()

def is_half_coverd(dict1, dict2):
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())

    common_keys = keys1 & keys2  # Intersection of keys
    coverage_ratio = len(common_keys) / len(keys1) if keys1 else 0  # Compute coverage, avoid division by zero

    return coverage_ratio >= 0.5


def all_values_zero(d):
    return all(float(value) == 0.0 for value in d.values())



