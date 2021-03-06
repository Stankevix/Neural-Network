# -*- coding: utf-8 -*-
"""MLP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_1po0iAGizYTnj8GI7lK58wBkivMJlnn

Nome: Gabriel Stankevix Soares

# DataSet - Credito Alemao

Conjunto de dados sobre emprestimo de crédito alemão.
Este conjunto de dados classifica o risco de credito de pessoas, por meio de 20 atributos, como risco bom ou risco ruim.

Classes
Bom 
Ruim 


É pior classificar  um cliente bom como ruim, do que classificar um cliente ruim quando ele é bom.

Este dataset foi escolhido por ser um tema recorrente no dia a dia e pela sua variedade de atributos disponiveis para analise e desenvolvimento de modelos.

**Descrição do atributo**

1. Situação da conta corrente existente, em marcos alemães.
2. Duração em meses
3. Histórico de crédito (créditos recebidos, pagos devidamente, atrasos, contas críticas)
4. Objetivo do crédito (carro, televisão, ...)
5. Montante de crédito
6. Situação da conta de poupança / títulos, em marcos alemães.
7. Emprego atual, em número de anos.
8. Taxa de parcelamento em porcentagem da renda disponível
9. Status pessoal (casado, solteiro, ...) e sexo
10. Outros devedores / fiadores
11. Atual residência desde X anos
12. Propriedade (por exemplo, imóveis)
13. Idade em anos
14. Outros planos de parcelamento (bancos, lojas)
15. Habitação (aluguel, próprio, ...)
16. Número de créditos existentes neste banco
17. Trabalho
18. Número de pessoas responsáveis ​​por fornecer manutenção para
19. Telefone (sim, não)
20. Trabalhador estrangeiro (sim, não)
"""

from google.colab import files

uploaded = files.upload()

"""## Analise Exploratoria de Dados"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io

sns.set(style="darkgrid")

credit = pd.read_csv(io.BytesIO(uploaded['dataset_31_credit-g.csv']))

credit.head()

"""Dataset eh composto por 700 pessoa com risco de credito bom e 300 pessoas com risco de credito mau."""

credit['class'].value_counts()

"""Ao total são 20 variaveis + classe que descrevem a pessoa com potencial de credito bom ou ruim"""

credit.info()

credit.describe()

"""Existe uma correlação forte positiva entre o tempo de duração do credito com o monte de valores solicitados, para as demais variaveis não foi possivel encontrar uma correlação sigfinicativa"""

credit_corr = credit.corr()

mask = np.triu(np.ones_like(credit_corr, dtype=bool))

f, ax = plt.subplots(1,figsize=(25, 5))

cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(credit_corr, mask=mask, cmap=cmap, vmax=.9, center=0,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})

plt.show()

"""Algumas caracteristicas interessantes neste dataset é que as pessoas com maior idade, mais tempo que duração de credito e com historico de emprestimos compoem a classe denominada como boa."""

sns.pairplot(credit,hue='class')

"""Como destaque das variveis categoricas a maior parte das pessoas ja tinha algum historico de credito pago, tanto boas quanto ruins.


"""

f, axes = plt.subplots(1, figsize=(12,5))
f = sns.countplot(x='credit_history', data=credit,ax=axes, hue='class')
plt.show()

"""Credito de compra são destinados principalmente para compra de radio/tv, carro novo ou mobilia. Pessoal com classe 'bad' ruim de credito tem maior incidencia em compra de carros novos"""

f, axes = plt.subplots(1, figsize=(18,5))
f = sns.countplot(x=credit.purpose, data=credit,ax=axes, hue='class')
plt.show()

"""Maioria das pessoas são trabalhadores qualificados 'skilled'"""

f, axes = plt.subplots(1, figsize=(12,5))
f = sns.countplot(x=credit.job, data=credit,hue='class',ax=axes)
plt.show()

"""# Modelagem

Escolha do algoritmo de RNAs foi a RNA chamada MLP ou Multiçayer Perceptron.

Este é um tipo clássico de rede neural composta por uma ou mais neurônio. Os dados são alimentados para uma camada de entrada, pode haver uma ou mais camadas ocultas fornecendo níveis de abstração e as previsões são feitas na camada de saída, também chamada de camada visível. 

Desta forma é adequado para resolver o nosso problema de classificação criando camadas e conexões entre as 20 variaveis disponveis para definir o rotulo ideal.

Neste estudo não será feito feature importance para selecionar as variaveis mais importantes.
"""

from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline

from sklearn.preprocessing import StandardScaler,OneHotEncoder,RobustScaler,MinMaxScaler
from sklearn.compose import ColumnTransformer

"""## Construção Pipeline

Dados foram divididos entre 30 % teste e 70 % treinamento, com 20 variaveis do tipo categorica e inteiro. A medida de performance padrão aplicada foi a acuracia e posteriormente medido a recall pois existe um alto custo associado a falso negativos neste problema.
"""

X = credit.drop("class", axis=1)
y = credit['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True, random_state=42, stratify=y)

numerical_features = X.select_dtypes("int64").columns
categorical_features = X.select_dtypes(include=['object']).columns

numeric_transformer = Pipeline(steps=[
    ('scaler', MinMaxScaler())])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)])

transf = preprocessor.fit(X)
transf

xtrain_prepared = transf.transform(X_train)
xtrain_prepared.shape

xtest_prepared = transf.transform(X_test)
xtest_prepared.shape

"""## MLP Model

Investigação feita neste modelo MLP foi para definir or melhores parametros para tax de aprendizado e o numero ideal de iterações que a rede precisa.
"""

mlp = MLPClassifier(max_iter=1000)

params_mlp = {
    'activation': ['identity', 'logistic', 'tanh', 'relu'],
    'solver': ['lbfgs','sgd','adam'],
    'learning_rate' : ['constant', 'invscaling', 'adaptive']
}


grid_mlp = GridSearchCV(estimator = mlp,
                       param_grid = params_mlp,
                       scoring ='accuracy',
                       cv = 2,
                       verbose = 1,
                       n_jobs = -1)

grid_mlp.fit(xtrain_prepared, y_train.ravel())

print('CV Score for best MLP Classifier model: {:.2f}'.format(grid_mlp.best_score_))

best_model_mlp = grid_mlp.best_estimator_
best_model_mlp

"""Modelo selecionado tem os parametros definidos como 

**learning_rate='adaptive'** - Mantém a taxa de aprendizagem constante referente ao valor de learning rate inicial enquanto a perda de treinamento continua diminuindo. 
Cada vez que duas epochs* consecutivas falham em diminuir a perda de treinamento ou falham em aumentar a pontuação de validação, a taxa de aprendizado atual é dividida por 5.

**activation='tanh'** - a função tan hiperbólica, retorna f (x) = tanh (x).

**solver='sgd'** - 'Sgd' refere-se à descida gradiente estocástica

*epochs:  é um hiperparâmetro que define o número de vezes que o algoritmo de aprendizado funcionará em todo o conjunto de dados de treinamento.

## Validacao Modelo
"""

from sklearn.metrics import accuracy_score,classification_report,recall_score

pipe = Pipeline(steps=[('preprocessor', preprocessor),
                      ('classifier', best_model_mlp)])

pipe.fit(X_train, y_train.ravel()) 

pred_test = pipe.predict(X_test)
accuracy_result = accuracy_score(y_test, pred_test)
    
print(classification_report(y_test, pred_test))

"""Algoritmo obteve uma performance boa, com acuracia de 76 % em teste. Porem é preciso avaliar que neste caso a recomendação de pessoas boas de credito como ruins deve acontecer em uma escala menor.

A metrica recall indicou um valor de 89 % de precisão na predição de pessoas boas de credito que realmente era boas de creditc, o que indica uma boa performance graças ao custo alto associado aos falso negativos.
"""