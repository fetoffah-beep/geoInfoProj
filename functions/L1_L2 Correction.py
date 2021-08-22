gamma = (1575.42 / 1227.)**2

if signal = L1C/A:
	delta_tsv_L1/CA = delta_tsv - T_GD
elif signal = L1_P(Y):
	delta_tsv_L1_P(Y) = delta_tsv - T_GD
elif signal = L2_P(Y):
	delta_tsv_L2_P(Y) = delta_tsv - (gamma * T_GD)

T_GD = (t_L1_PY - t_L2_PY) * 1 / (1-gamma)