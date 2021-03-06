import numpy as np


def check_finite_differences(fwd_fn, bwd_fn, delta=1e-5, n_times=10, gen_input_fn=None, test_inputs=(0, ), test_outputs=None, aux_only=False):
    """Check that the analytical gradient `bwd_fn` matches the true gradient.
    It is verified using the finite differences method on fwd_fn..
    :param fwd_fn:
    :param bwd_fn:
    :param delta:
    :param n_times:
    :param extra_args:
    :param gen_input_fn:
    :returns True if all gradient checks were ok, False if some failed
    """
    assert gen_input_fn != None

    def compute_output(ys, out_weights):
        res = 0.0
        for i in range(len(ys)):
            res += (ys[i] * out_weights[i]).sum()

        return res


    for n in range(n_times):
        rand_input = gen_input_fn()

        ys, out_aux = fwd_fn(rand_input)
        out_weights = tuple(np.random.randn(*y.shape) for y in ys)
        if test_outputs is not None:
            for i, ow in enumerate(out_weights):
                if not i in test_outputs:
                    ow[:] = 0

        assert aux_only
        grads = bwd_fn(out_aux, out_weights)

        for i in test_inputs:
            assert grads[i].shape == rand_input[i].shape, "shape1=%s, shape2=%s" % (grads[i].shape,  rand_input[i].shape, )

            for dim, x in enumerate(rand_input[i].flat):
                orig = rand_input[i].flat[dim]

                rand_input[i].flat[dim] = orig + delta
                (ys, _) = fwd_fn(rand_input)
                out1 = np.array([(ys[ii] * out_weights[ii]).sum() for ii in range(len(ys))]).sum()

                rand_input[i].flat[dim] = orig - delta
                (ys, _) = fwd_fn(rand_input)
                out2 = np.array([(ys[ii] * out_weights[ii]).sum() for ii in range(len(ys))]).sum()

                rand_input[i].flat[dim] = orig

                grad_num = ((out1 - out2) / (2 * delta))
                grad_an = grads[i].flat[dim]

                if abs(grad_num) < 1e-7 and abs(grad_an) < 1e-7:
                    print 'inp', i, 'dim', dim, 'GRADIENT WARNING: gradients too small (num: %.10f, an: %.10f)' % (grad_num, grad_an, )
                else:
                    rel_error = abs(grad_an - grad_num) / abs(grad_an + grad_num)
                    if rel_error > 1e-2:
                        print 'GRADIENT WARNING', 'inp', i, 'dim', dim, 'val', x,
                        print 'an', grad_an, 'num', grad_num,
                        print 'rel error', rel_error,
                        if rel_error > 1:
                            print 'GRADIENT ERROR TOO LARGE!'
                            return False
                        print
                    else:
                        #print 'GRADIENT OK', 'inp', i, 'dim', dim, 'x', x, 'an', grad_an, 'num', grad_num
                        pass


    return True


class TestParamGradInLayer:
    """Wrap given layer into a layer that accepts its parameter as input.
    Useful for gradient checking by check_finite_differences."""
    def __init__(self, layer, param_name, layer_input):
        self.param_name = param_name
        self.layer = layer
        self.orig_shape = layer.params[param_name].shape
        self.layer_input = layer_input

    def gen(self):
        return np.random.randn(*self.orig_shape)

    def forward(self, (x, )):
        #orig = self.layer.params[self.param_name].copy()
        self.layer.params[self.param_name][:] = x
        res = self.layer.forward(self.layer_input)
        #self.layer.params[self.param_name][:] = orig

        return res

    def backward(self, aux, grads):
        self.layer.grads.zero()

        self.layer.backward(aux, grads)

        return (self.layer.grads[self.param_name], )





import time

def timeit(method):
    return method

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print 'timing: %r %r %2.2f sec' % \
              (method.__code__.co_filename, method.__name__, te-ts)
        #(method.__name__, args, kw, te-ts)
        return result

    return timed
