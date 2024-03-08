from scipy.stats import norm, invgamma, gamma
import numpy as np
import matplotlib.pyplot as plt

#Question 1
# Define the relevant values
y = 0.7
a = 10
b = 10
n = 10000
burn = 1000

# Initialize
theta_1 = 0
theta_2 = 0
v2 = 1

# Define lists
theta_1_samples = []
theta_2_samples = []
v2_samples = []

# Use Gibbs Sampling to Determine Solutions
for i in range(n):
    u_theta_1 = (y-theta_2)/(1+1/v2)
    var_theta_1 = 1/(1+1/v2)
    theta_1 = norm.rvs(u_theta_1, var_theta_1**0.5)

    u_theta_2 = (y-theta_1)/(1+1/v2)
    var_theta_2 = 1/(1+1/v2)
    theta_2 = norm.rvs(u_theta_2, var_theta_2**0.5)

    a2 = a + 1
    b2 = b + 0.5*(theta_1**2 + theta_2**2)
    v2 = invgamma.rvs(a2, scale=b2)

    # Update Lists
    theta_1_samples.append(theta_1)
    theta_2_samples.append(theta_2)
    v2_samples.append(v2)

# Discard Relevant Samples
theta_1_samples = theta_1_samples[burn:]
theta_2_samples = theta_2_samples[burn:]
v2_samples = v2_samples[burn:]

# Create Plots for Marginal Posterior Densities
fig, plot = plt.subplots(3, 1, figsize=(10, 15))
plot[0].hist(theta_1_samples, bins=50, density=True, color='blue')
plot[0].set_title('Marginal Posterior of $\\theta_1$')
plot[0].set_xlabel('Value')
plot[0].set_ylabel('Density')

plot[1].hist(theta_2_samples, bins=50, density=True, color='blue')
plot[1].set_title('Marginal Posterior of $\\theta_2$')
plot[1].set_xlabel('Value')
plot[1].set_ylabel('Density')

plot[2].hist(v2_samples, bins=50, density=True, color='blue')
plot[2].set_title('Marginal Posterior of $V^2$')
plot[2].set_xlabel('Value')
plot[2].set_ylabel('Density')

# Find 95% Credible Set
cs_theta_1 = np.percentile(theta_1_samples, [2.5, 97.5])
cs_theta_2 = np.percentile(theta_2_samples, [2.5, 97.5])
cs_v2 = np.percentile(v2_samples, [2.5, 97.5])

# Show CS on Plots
plot[0].axvline(cs_theta_1[0], color='r', linestyle='--')
plot[0].axvline(cs_theta_1[1], color='r', linestyle='--', label='95% Credibility Set')
plot[0].legend()
plot[1].axvline(cs_theta_2[0], color='r', linestyle='--')
plot[1].axvline(cs_theta_2[1], color='r', linestyle='--', label='95% Credibility Set')
plot[1].legend()
plot[2].axvline(cs_v2[0], color='r', linestyle='--')
plot[2].axvline(cs_v2[1], color='r', linestyle='--', label='95% Credibility Set')
plot[2].legend()

# Show CS Values
# Set Areas for Text
size_theta_1, _, _ = plot[0].hist(theta_1_samples, bins=50, density=True)
size_theta_2, _, _ = plot[1].hist(theta_2_samples, bins=50, density=True)
size_v2, _, _ = plot[2].hist(v2_samples, bins=50, density=True)

text_theta_1 = size_theta_1.max() * 0.3
text_theta_2 = size_theta_2.max() * 0.3
text_v2 = size_v2.max() * 0.3

for i, (cs, max_height) in enumerate(zip([cs_theta_1, cs_theta_2, cs_v2], [text_theta_1, text_theta_2, text_v2])):
    plot[i].axvline(cs[0], color='r', linestyle='--')
    plot[i].axvline(cs[1], color='r', linestyle='--', label='95% CI')
    plot[i].text(cs[0], max_height, f'{cs[0]:.2f}', horizontalalignment='center', verticalalignment='bottom')
    plot[i].text(cs[1], max_height, f'{cs[1]:.2f}', horizontalalignment='center', verticalalignment='bottom')

# Plot Figures
plt.tight_layout
plt.show()



# Question 2
# Define values
m = 2
t = 0.5
obs = np.array([-2, -1, 5, -7, 0, 4, 2])
n = 10000
burn = 500

# Prior Distribution
def prior_dist(theta, m):
    return (1/m) * np.cos((np.pi * theta)/(2 * m))**2

# Likelihoof Function
def likelihood(theta, obs, t):
    return np.sqrt(t) * np.exp(-t/2 * np.sum((obs - theta)**2))

# Metrolopolis Algorithm
def metro(obs, m, t, n, burn):
    samples = np.zeros(n)
    theta_0 = np.random.uniform(-m, m)

    for x in range(n):
        theta_prop = np.random.uniform(-m, m)
        metro_ratio = (likelihood(theta_prop, obs, t) * prior_dist(theta_prop, m)) /\
                       (likelihood(theta_0, obs, t) * prior_dist(theta_0, m))

        if np.random.rand() < metro_ratio:
            theta_0 = theta_prop

        samples[x] = theta_0

    # Discard First 500 Samples
    return samples[burn:]

# Run Algorithm
samples = metro(obs, t, m, n, burn)

# Plot the Figures
plt.hist(samples, bins=50, density=True)
plt.title('Posterior Distribution of $\\theta$')
plt.xlabel('$\\theta$')
plt.ylabel('Density')

# Show 95% Credible Set and Values on Plot
lower, upper = np.percentile(samples, [2.5, 97.5])
plt.axvline(lower, color='red', linestyle='--', label='95% Credible Set')
plt.axvline(upper, color='red', linestyle='--')

plt.text(lower, plt.ylim()[1]*0.85, f'{lower: .2f}', horizontalalignment='right', color='black')
plt.text(upper, plt.ylim()[1]*0.85, f'{upper: .2f}', horizontalalignment='left', color='black')

plt.legend()
plt.show()

# Find Bayes Estimator of Posterior Samples
bayes = np.mean(samples)
cs = np.percentile(samples, [2.5, 97.5])

print(bayes, cs)



# Question 3
# Take in Data as Lists
high_protein = [134, 146, 104, 119, 124, 161, 107, 83, 133, 129, 97, 123]
low_protein = [70, 118, 101, 85, 107, 132, 94]

# Values
theta10 = theta20 = 110
t10 = t20 = 1/100
a1 = a2 = 0.01
b1 = b2 = 4
n = 10000
burn = 500

# Initialize Values
theta1 = theta10
theta2 = theta20
t1 = t10
t2 = t20

# Initialize Sample Lists
theta_1_samples = []
theta_2_samples = []
t1_samples = []
t2_samples = []

# Gibbs Sampler Algorithm
for x in range(n):
    # Theta 1
    var_theta1 = 1 / (len(high_protein)/t1 + 1/t10)
    u_theta1 = var_theta1 * (sum(high_protein)/t1 + theta10/t10)
    theta1 = norm.rvs(loc=u_theta1, scale=np.sqrt(var_theta1))

    # Theta 2
    var_theta2 = 1 / (len(low_protein)/t2 + 1/t20)
    u_theta2 = var_theta2 * (sum(low_protein)/t2 + theta20/t20)
    theta2 = norm.rvs(loc=u_theta2, scale=np.sqrt(var_theta2))

    # Tau1
    alpha1 = a1 + len(high_protein)/2
    beta1 = b1 + 0.5 * sum([(p - theta1)**2 for p in high_protein])
    t1 = gamma.rvs(a=alpha1, scale=1/beta1)

    # Tau2
    alpha2 = a2 + len(low_protein)/2
    beta2 = b2 + 0.5 * sum([(p - theta2)**2 for p in low_protein])
    t2 = gamma.rvs(a=alpha2, scale=1/beta2)

    # Store Samples
    theta_1_samples.append(theta1)
    theta_2_samples.append(theta2)
    t1_samples.append(t1)
    t2_samples.append(t2)

# Discard First 500 Samples
theta_1_samples = theta_1_samples[burn:]
theta_2_samples = theta_2_samples[burn:]
t1_samples = t1_samples[burn:]
t2_samples = t2_samples[burn:]

# Find Theta1 - Theta2 and Show Proportion of Positive Differences
differences = [theta1 - theta2 for theta1, theta2 in zip(theta_1_samples, theta_2_samples)]
positive_amount = sum(1 for difference in differences if difference > 0)/len(differences)

# Plot relevant data
plt.figure(figsize=(10, 5))
plt.hist(differences, bins=50, alpha=0.9, label='$\\theta_1$ - $\\theta_2$')
plt.title('Posterior Distribution of $\\theta_1$ - $\\theta_2$')
plt.xlabel('$\\theta_1$ - $\\theta_2$')
plt.ylabel('Frequency')

# Find and Show 95% Credible Set and Values on Plot
differences_sorted = sorted(differences)
lower = differences_sorted[int(len(differences_sorted) * 0.025)]
upper = differences_sorted[int(len(differences_sorted) * 0.975) - 1]
plt.axvline(lower, color='red', linestyle='--', label='95% Credible Set Lower')
plt.axvline(upper, color='black', linestyle='--', label='95% Credible Set Upper')

plt.text(lower, plt.ylim()[1]*0.25, f'{lower: .2f}', horizontalalignment='right', color='black')
plt.text(upper, plt.ylim()[1]*0.25, f'{upper: .2f}', horizontalalignment='left', color='black')

plt.legend()
plt.show()

print("Proportion of Positive Differences: {}, 95% Credibility Set: [{},{}]".format(positive_amount, lower, upper))