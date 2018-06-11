import numpy as np
import re
import pdb

from collections import defaultdict as dd

from sklearn.feature_extraction.text import CountVectorizer as CV
from sklearn.preprocessing import LabelEncoder as LE

from . import Inferencer
from .algorithm.active_learning import active_learning
from ..metadata_interface import *


def get_name_features(names):

        name = []
        for i in names:
            s = re.findall('(?i)[a-z]{2,}',i)
            name.append(' '.join(s))

        cv = CV(analyzer='char_wb', ngram_range=(3,4))
        fn = cv.fit_transform(name).toarray()

        return fn


class ActiveLearningInterface(Inferencer):

    def __init__(self,
        target_building,
        target_srcids,
        fold,
        rounds
        ):

        super(ActiveLearningInterface, self).__init__(
            target_building=target_building,
            target_srcids=target_srcids
        )

        srcids = [point['srcid'] for point
                  in LabeledMetadata.objects(building=target_building)]
        pt_type = [LabeledMetadata.objects(srcid=srcid).first().point_tagset
                   for srcid in srcids]
        pt_name = [RawMetadata.objects(srcid=srcid).first()\
                   .metadata['VendorGivenName'] for srcid in srcids]
        fn = get_name_features(pt_name)

        le = LE()
        try:
            label = le.fit_transform(pt_type)
        except:
            pdb.set_trace()

        #TODO: add processing for transferred info
        transfer_fn = None
        transfer_label = None

        #print ('# of classes is %d'%len(np.unique(label)))
        print ('running active learning by Hong on building %s'%target_building)
        print ('%d instances loaded'%len(pt_name))


        self.learner = active_learning(
            fold,
            rounds,
            #2 * len( np.unique(label) ),
            28,
            fn,
            label,
            transfer_fn
            transfer_label
        )


    def example_set():
        #TODO: get a set of example IDs that the user can provide label for, i.e, the set of examples to run AL
        pass


    def get_label(idx):
        #TODO: get the label for the example[idx] from human
        pass


    def select_example(self):

        idx, c_idx = self.learner.select_example()

        return idx


    def update_model(self, srcid, cluster_id):

        self.learner.labeled_set.append(srcid)
        self.learbner.new_ex_id = srcid
        self.learner.cluster_id = cluster_id
        self.learner.update_model()


    def predict(self, target_srcids):

        return self.learner.clf.predict(target_srcids)


    def learn_auto(self):

        self.learner.run_CV()

