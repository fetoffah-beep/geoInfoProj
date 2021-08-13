
# For the Li_P signal
gamma = math.pow((1575.42 / 1227.6), 2)
PR = (PR_i2 - gamma * PR_i1) / (1 - gamma) #where i is the channel, L1, L2 etc.