import tensorflow as tf
from tensorflow.keras import layers

def create_actor(state_size, action_size):
    # State size: Dimension of the state space
    # Action size: Dimension of the action space
    model = tf.keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=(state_size,)),
        layers.Dense(128, activation='relu'),
        layers.Dense(action_size, activation='sigmoid')  # Use sigmoid/softmax if actions are discrete/categorical
    ])
    return model
