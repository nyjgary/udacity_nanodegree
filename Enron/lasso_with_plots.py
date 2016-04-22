from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LassoCV
from sklearn.linear_model import lasso_path

alphas = np.logspace(-6, 1, 50)
data = featureFormat(dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

lasso = make_pipeline(MinMaxScaler(), 
                      LassoCV(random_state = 42, cv=50, copy_X = True, alphas = alphas)).fit(features, labels)
sfm = SelectFromModel(lasso.steps[1][1], prefit=True)
features_lasso = sfm.transform(features)
n_features_lasso = features_lasso.shape[1]
alpha_lasso = -np.log10(lasso.steps[1][1].alpha_)

plt.figure(figsize=(16,8))

# Plot MSE by alpha 
plt.subplot(121)
m_log_alphas = -np.log10(lasso.steps[1][1].alphas_)
plt.plot(m_log_alphas, lasso.steps[1][1].mse_path_, ':')
plt.plot(m_log_alphas, lasso.steps[1][1].mse_path_.mean(axis=-1), 'k',
         label='Average across the folds', linewidth=2)
plt.axvline(-np.log10(lasso.steps[1][1].alpha_), linestyle='--', color='k',
            label='alpha: CV estimate')
plt.legend(loc = 'upper left')
plt.xlabel('-Log(alpha)')
plt.ylabel('Mean square error')
plt.title('Mean square error on each fold')
plt.axis('tight')

# Plot lasso paths 
plt.subplot(122)
alphas_lasso, coefs_lasso, _ = lasso_path(features, labels, alphas = alphas)
plt.plot(-np.log10(alphas_lasso), coefs_lasso.T)
plt.axvline(-np.log10(lasso.steps[1][1].alpha_), linestyle='--', color='k',
            label='alpha: CV estimate')
plt.xlabel('-Log(alpha)')
plt.ylabel('Coefficients')
plt.title('Lasso Paths')
plt.axis('tight')

lasso_coef = pd.DataFrame({'coef': lasso.steps[1][1].coef_.tolist()}, features_list[1:]).round(3) 
lasso_selection = lasso_coef[lasso_coef['coef']!=0]
lasso_selection

print "Lasso selected an alpha of %.2f with %d features:" % (alpha_lasso, len(lasso_selection)) 
lasso_selection.sort('coef', ascending=False)

features_logit = ['poi'] + lasso_selection.index.tolist() 
test_classifier(make_pipeline(MinMaxScaler(), LogisticRegression()), dataset, features_logit, folds = 1000)