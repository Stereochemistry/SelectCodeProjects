import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gamma, beta
import pymc as pm

#Question 1c
x = np.linspace(0, 1, 1000000)
a, b = 5, 38.5
low, high = 0.0246, 0.2741
pdf = gamma.pdf(x, a=a, scale=1 / b)

y_max = max(pdf)
x_max = x[pdf.argmax()]
print(x_max, y_max)

# density curve
plt.plot(x, pdf, color="black", label="PDF")

# additional markings
plt.plot(x, np.full_like(x, 0.857), "r-", label="$k(\\alpha)$")
plt.axvline(low, linestyle="dashed", linewidth=1, label="Set boundaries")
plt.axvline(high, linestyle="dashed", linewidth=1)

plt.fill_between(
    x,
    pdf,
    where=(low < x) & (x < high),
    color="lightgrey",
    label="HPD-credible region",
)
plt.legend()
plt.title("95% HPD credible set of a Gamma(5, 38.5) distribution")
plt.ylim(bottom=0)
plt.xlim(left=0, right=0.6)
plt.text(low + 0.01, 6.55, f"{low:.3f}", rotation=0)
plt.text(high + 0.01, 6.55, f"{high:.3f}", rotation=0)
plt.show()

lower_eqt = gamma.ppf(0.025, a, scale=1 / b)
upper_eqt = gamma.ppf(0.975, a, scale=1 / b)

# density curve
plt.plot(x, pdf, color="black", label="PDF")

# additional markings
plt.plot(
    [lower_eqt, upper_eqt],
    [gamma.pdf(lower_eqt, a, scale=1 / b), gamma.pdf(upper_eqt, a, scale=1 / b)],
    "r-",
    linewidth=1,
)
plt.axvline(lower_eqt, linestyle="dashed", linewidth=1, label="Set boundaries")
plt.axvline(upper_eqt, linestyle="dashed", linewidth=1)

plt.fill_between(
    x,
    pdf,
    where=(lower_eqt < x) & (x < upper_eqt),
    color="lightgrey",
    label="Equitailed credible region",
)
plt.legend()
plt.title("95% Equitailed credible set of a Gamma(5, 38.5) distribution")
plt.ylim(bottom=0)
plt.xlim(left=0, right=0.6)
plt.text(lower_eqt + 0.01, 6.55, f"{lower_eqt:.3f}", rotation=0)
plt.text(upper_eqt - 0.055, 6.55, f"{upper_eqt:.3f}", rotation=0)
plt.show()



#Question 2b
y = np.linspace(0, 1, 1000000)
a, b = 54.5, 10.5
low, high = 0.8, 1
pdf = beta.pdf(y, a=a, b=b)

lower_eqt = beta.ppf(0.025, a, b)
upper_eqt = beta.ppf(0.975, a, b)

# density curve
plt.plot(y, pdf, color="black", label="PDF")

# additional markings
plt.plot(
    [lower_eqt, upper_eqt],
    [beta.pdf(lower_eqt, a, b), beta.pdf(upper_eqt, a, b)],
    "r-",
    linewidth=1,
)
plt.axvline(lower_eqt, linestyle="dashed", linewidth=1, label="Set boundaries")
plt.axvline(upper_eqt, linestyle="dashed", linewidth=1)

plt.fill_between(
    y,
    pdf,
    where=(lower_eqt < y) & (y < upper_eqt),
    color="lightgrey",
    label="Credible region",
)
plt.legend()
plt.title("95% credible set of a Beta(54.5, 10.5) distribution")
plt.ylim(bottom=0)
plt.xlim(left=0.6, right=1.0)
plt.text(lower_eqt, 6.55, f"{lower_eqt:.3f}", rotation=0)
plt.text(upper_eqt, 6.55, f"{upper_eqt:.3f}", rotation=0)
plt.show()



#Question 2c
# Observations
n = 30  # Patients
k = 23  # Responders

def prob_model():
    with pm.Model() as model:
        # Define the Beta Prior
        p = pm.Beta('p', alpha=31.5, beta=3.5)

        # Define the likelihood
        L = pm.Binomial('L', n=n, p=p, observed=k)

        # Sample Posterior
        dist = pm.sample(1000, tune=2000, return_inferencedata=False)

    prob_H0 = np.mean(dist['p'] >= 0.8)
    prob_H1 = 1 - prob_H0

    print("The odds of H_0 and H_1 are {} and {}, respectively".format(prob_H0, prob_H1))

if __name__ == '__main__':
    prob_model()