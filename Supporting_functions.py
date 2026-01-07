

def putDictInDict(dict,key1, key2,value):
    if key1 not in dict:
        dict_second = {}
        dict_second[key2] = value
        dict[key1] = dict_second
    else:
        dict_second = dict[key1]
        if key2 in dict_second and dict_second[key2] != value:
            print(key1 + "+" + key2 + ":with different value")
        dict_second[key2] = value
        dict[key1] = dict_second

def readMatrix_withZero(file,id_index):
    dict_gene_id_inten = {}
    fr = open(file,"r")
    dict_id = {}
    list_id = []
    list_gene = []
    for line in fr.readlines():
        if line.startswith("Gene_symbol\t") or line.startswith("ID\t") or line.startswith("Name\t") \
                or line.startswith("ROW_ID\t") or line.startswith("Gene\t")\
                or line.startswith("#ID\t") or line.startswith("idx")\
                or line.startswith("geneSymbol")\
                or line.startswith("set")or line.startswith("Gene_name") or line.startswith("Index")\
                or line.startswith("gene_symbol\t"):
            sp = line.strip().split("\t")
            for i in range(len(sp))[id_index:]:
                dict_id[i] = str(sp[i])
                list_id.append(sp[i])
        else:
            sp = line.strip().split("\t")
            gene = str(sp[0])
            for i in range(len(sp))[id_index:]:
                if sp[i] != "NA" and sp[i] != "":
                    inten = sp[i]
                    id = dict_id[i]
                    putDictInDict(dict_gene_id_inten,gene,id,inten)
            if gene in dict_gene_id_inten:
                list_gene.append(gene)
    #print(list_id)
    print("Total element\t" + str(len(list_gene)))
    print("Be careful!! do you want to keep 0.0 or not? 0.0 was excluded from this version")
    return dict_gene_id_inten,list_gene,list_id