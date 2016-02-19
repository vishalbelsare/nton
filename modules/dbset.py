import numpy as np

import nn
from db_dist import DBDist


class DBSet(nn.Block):
    def __init__(self, index_content, contents, vocab, entry_vocab):
        self.index_db = DBDist(index_content, vocab, entry_vocab)

        self.content_dbs = []
        for content in contents:
            self.content_dbs.append(DBDist(content, entry_vocab, vocab))

    def forward(self, inputs):
        assert type(inputs) == tuple
        assert len(inputs) == self.index_db.n, "Len inputs: %d, index_db.n: %d" % (len(inputs), self.index_db.n,)

        ((entry_dist, ), entry_dist_aux) = self.index_db.forward(inputs)
        count = len(entry_dist[entry_dist == np.max(entry_dist)])

        ((entry_dist, ), entry_dist_amplify_aux) = nn.Amplify.forward((entry_dist,))
        nn.DEBUG.add_db_entry_dist(entry_dist)




        res = []; res_aux = []
        for content_db in self.content_dbs:
            ((db_val, ), db_val_aux) = content_db.forward((entry_dist, ))
            res.append(db_val); res_aux.append(db_val_aux)

        return ((entry_dist, ) + tuple(res), nn.Vars(
            res=res_aux,
            entry_dist=entry_dist_aux,
            entry_dist_amplify=entry_dist_amplify_aux,
            count=count
        ))

    def backward(self, aux, dres):
        dentry_dist = dres[0].copy()

        lst_dentry_dist = []
        for ddb_val, res_aux, content_db in zip(dres[1:], aux['res'], self.content_dbs):
            self.accum_grads((lst_dentry_dist, ), content_db.backward(res_aux, (ddb_val, )))

        dentry_dist += sum(lst_dentry_dist)

        (dentry_dist, ) = nn.Amplify.backward(aux['entry_dist_amplify'], (dentry_dist,))

        dinputs = self.index_db.backward(aux['entry_dist'], (dentry_dist, ))

        return dinputs







