import matplotlib.pyplot as plt
import numpy as np




# PoC lineage length data
data = [
[4, 6, 5, 5, 4, 5, 6, 4, 4, 4, 4, 4, 7, 4, 5, 5, 4, 4, 6, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 5, 5, 5, 4, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 5, 4, 4, 4, 5, 4, 5, 5, 5, 5, 5, 5, 4, 5, 4, 5],
[4, 5, 5, 4, 5, 4, 4, 5, 3, 4, 5, 5, 4, 5, 4, 4, 5, 4, 4, 5, 5, 4, 5, 6, 4, 4, 5, 5, 5, 4, 4, 4, 4, 5, 4, 4, 4, 5, 4, 4, 5, 4, 4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 4, 5, 5, 5, 4, 5, 4, 5, 4, 5, 4, 4, 4, 5, 4, 5, 5, 4, 4, 4, 4, 4, 5, 4],
[5, 4, 6, 7, 5, 6, 7, 7, 6, 5, 5, 4, 5, 6, 4, 5, 6, 8, 7, 6, 8, 7, 6, 7, 6, 6, 5, 6, 5, 6, 6, 5, 5, 7, 4, 7, 6, 5, 7, 5, 6, 7, 6, 5, 4, 6, 5, 7, 5, 6, 5, 4, 5, 5, 6, 6, 6, 6, 5, 6, 6, 6, 6, 4, 5, 5, 6, 5, 6, 5, 5, 6, 7, 5, 7, 4, 6, 6, 6, 5, 5, 10, 7, 6, 6],
[6, 5, 5, 5, 5, 7, 6, 5, 6, 6, 5, 4, 5, 6, 5, 5, 6, 4, 7, 5, 5, 5, 5, 7, 7, 5, 5, 5, 5, 5, 5, 5, 4, 5, 4, 5, 4, 4, 6, 5, 5, 4, 6, 6, 6, 4, 5, 5, 4, 4, 6, 6, 5, 6, 4, 5, 7, 6, 6, 4, 4, 5, 5, 4, 5, 6],
[6, 3, 3, 3, 12, 13, 3, 3, 4, 11, 2, 3, 2, 4, 8, 3, 4, 3, 3, 7, 2, 3, 3, 3, 5, 3, 3, 9, 14, 9, 8, 3, 7, 6, 3, 9, 3, 3, 3, 3, 7, 3, 3, 9, 7, 3, 4, 3, 3, 3, 2, 2, 8, 10, 7, 9, 2, 3, 4, 3, 11, 2, 4, 13, 3, 3, 5, 5, 3, 3, 3, 2, 3, 6],
[7, 9, 7, 8, 7, 10, 22, 7, 10, 9, 10, 8, 8, 10, 8, 9, 6, 8, 10, 9, 6, 9, 11, 11, 7, 8, 8, 9, 8, 9, 9, 8, 9, 12, 8, 8, 10, 7, 8, 12, 11, 15, 9, 7, 6, 21, 14, 9, 8, 7, 7, 13, 8, 9, 13, 8, 9, 9, 11, 13, 7, 9, 8, 7, 8, 10, 8, 6, 6, 7, 7, 7, 7, 8, 7, 9, 6]
]



x_labels = ["CVE-2016-4487", "CVE-2016-4490","CVE-2016-4489", "CVE-2016-4492", "CVE-2017-9047", "CVE-2018-8807"]

fig, ax=plt.subplots()
box = ax.boxplot(data)


ax.set_xticks(range(1, len(x_labels)+1))
plt.xticks(range(1, len(x_labels)+1), x_labels, rotation=45)


plt.title("Lineage Length Analysis")
plt.xlabel('Vulnerability')
plt.ylabel('Lineage Length')


plt.tight_layout()


plt.savefig('./PoC-lineage-analysis/lineage-length-box.png')










plt.cla()

dataa = []
for i in data:
    dataa = dataa + i
plt.hist(dataa, bins=12, density=True) 


plt.title("Lineage Length Distribution Histogram")
plt.xlabel("Proportion")
plt.ylabel("Lineage Length")
plt.tight_layout()
plt.savefig('./draw-0816/lineage-length-hist.png')

plt.figure()

data_set = list(set(dataa))
b = [0 for i in range(max(data_set)+1)]
for i in data_set:
    b[i] = dataa.count(i) / len(dataa)

plt.title("Lineage Length Distribution Histogram")
plt.ylabel("Proportion")
plt.xticks(range(0, len([str(x) for x in range(23)])), [str(x) for x in range(23)])
plt.xlabel("Lineage Length")
plt.tight_layout()

plt.bar(range(len(b)), b)
plt.savefig('./draw-0816/lineage-length-bar.eps')
