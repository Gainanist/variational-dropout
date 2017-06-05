import tensorflow as tf
import numpy as np


def clip(x):
	return tf.clip_by_value(x, -8, 8)
	
	
def weight_matrix(num_in, num_out):
	with tf.variable_scope("weight"):
		d = np.sqrt(6.0)/np.sqrt(num_in+num_out)
		v = tf.Variable(tf.random_uniform(shape=[num_in, num_out], minval=-d, maxval=d))
		tf.add_to_collection('weights', v)
		return v


def bias_vector(num_out):
	with tf.variable_scope("bias"):
		v = tf.Variable(tf.zeros(shape=[num_out]))
		tf.add_to_collection('biases', v)
		return v


class FCVarDropout():
	def __init__(self, num_in, num_out, nonlinearity, ard_init=-10):
		self.reg = True
		self.W = weight_matrix(num_in, num_out)
		self.b = bias_vector(num_out)
		self.nonlinearity = nonlinearity
		# ARD is Automatic Relevance Determination
		self.log_sigma2 = tf.Variable(ard_init*tf.ones([num_in, num_out]), 'ls2')


	def get_output(self, x, deterministic, train_clip=False, thresh=3):
		# Alpha is the dropout rate
		log_alpha = clip(self.log_sigma2 - tf.log(self.W ** 2))
		
		# Values of log_alpha that are above the threshold
		clip_mask = tf.greater_equal(log_alpha, thresh)

		def true_path(): # For inference
			# If log_alpha >= thresh, return 0
			# If log_alpha < thresh, return tf.matmul(x,self.W)
			return tf.matmul(x, tf.where(clip_mask, tf.zeros_like(self.W), self.W))
		
		def false_path(): # For training
			# Sample from a normal distribution centred on tf.matmul(x,W)
			# and with variance roughly proportional to the size of tf.matmul(x,W)*tf.exp(log_alpha)
			W = self.W
			if train_clip:
				raise NotImplementedError
			mu = tf.matmul(x,W)
			si = tf.sqrt(tf.matmul(x*x, tf.exp(log_alpha) * self.W * self.W)+1e-8)
			return mu + tf.random_normal(tf.shape(mu), mean=0.0, stddev=1.0) * si
			
		activation = tf.cond(deterministic, true_path, false_path)
		return self.nonlinearity(activation + self.b)
		
		
class Conv2DDropout():
	def __init__(self):
		pass