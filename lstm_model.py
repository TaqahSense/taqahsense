import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# 1. تحميل البيانات
print("Loading cleaned dataset...")
df = pd.read_csv("cleaned_household_power.csv")

# 2. تجهيز البيانات وتجمعيها بالساعة لسرعة التدريب
df['datetime'] = pd.to_datetime(df['datetime'])
df = df.set_index('datetime')
hourly_df = df[['global_active_power']].resample('1h').mean().dropna()

# 3. تحجيم البيانات (Scaling) لأن LSTM يعمل بشكل أفضل مع القيم بين 0 و 1
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(hourly_df)

# 4. تحويل البيانات إلى تسلسلات زمنيّة (Sequence Generation)
# نستخدم آخر 24 ساعة لتوقع الساعة القادمة
LOOKBACK = 24

X, y = [], []
for i in range(LOOKBACK, len(scaled_data)):
    X.append(scaled_data[i-LOOKBACK:i, 0])
    y.append(scaled_data[i, 0])

X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 1))

# 5. تقسيم البيانات إلى تدريب واختبار (آخر 72 ساعة للاختبار)
train_size = len(X) - 72
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 6. بناء نموذج LSTM
print("Building LSTM Model Architecture...")
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=False),
    Dropout(0.2),
    Dense(units=1) # المخرج: التنبؤ بقيمة الاستهلاك
])

model.compile(optimizer='adam', loss='mean_squared_error')

# 7. تدريب النموذج
print("Training LSTM model...")
model.fit(X_train, y_train, epochs=15, batch_size=32, validation_split=0.1, verbose=1)

# 8. التنبؤ وتقييم الخطأ (RMSE)
predictions = model.predict(X_test)

# إعادة التحجيم إلى القيم الأصلية
predictions_actual = scaler.inverse_transform(predictions)
y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

rmse = np.sqrt(mean_squared_error(y_test_actual, predictions_actual))

print("--------------------------------------------------")
print(f" LSTM Model Evaluation Completed!")
print(f" Root Mean Squared Error (RMSE): {rmse:.4f}")
print("--------------------------------------------------")

# 9. حفظ النموذج والمُحجّم (Scaler)
model.save("lstm_power_forecasting_model.h5")
joblib.dump(scaler, "lstm_scaler.pkl")

print(" Model saved successfully as 'lstm_power_forecasting_model.h5'")