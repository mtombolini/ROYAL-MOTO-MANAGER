import tensorflow as tf
from tensorflow.keras import layers

def create_critic(state_size, action_size):
    # Input layers for state and action
    state_input = layers.Input(shape=(state_size,))
    action_input = layers.Input(shape=(action_size,))
    concat = layers.Concatenate()([state_input, action_input])
    
    # Critic network to evaluate the action-state pair
    out = layers.Dense(128, activation='relu')(concat)
    out = layers.Dense(128, activation='relu')(out)
    out = layers.Dense(1)(out)  # Output is the value of the state-action pair
    
    model = tf.keras.Model(inputs=[state_input, action_input], outputs=out)
    return model