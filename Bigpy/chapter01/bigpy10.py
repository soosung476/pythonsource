import matplotlib.pyplot as plt

temperatures = [3.3,34.5,14.2,-10]
x = list(range(4))
x_lables = ['Spring','Summer','Fall','Winter']

# bar chart
plt.title("Bar Chart")
plt.bar(x, temperatures)
plt.xticks(x, x_lables)
plt.yticks(sorted(temperatures))
plt.xlabel("seasons")
plt.ylabel("temperatures")
plt.show()