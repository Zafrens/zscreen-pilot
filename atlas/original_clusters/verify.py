"""Verify cluster identities and centroids from released core inputs."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    package=args.package.resolve(); atlas=package/'atlas/original_clusters'
    members=pd.read_parquet(atlas/'members.parquet')
    csv_members=pd.read_csv(atlas/'members.csv')
    pd.testing.assert_frame_equal(members,csv_members,check_dtype=False)
    keys=pd.read_csv(atlas/'centroid_keys.csv')
    census=pd.read_csv(atlas/'census.csv')
    original=pd.read_csv(package/'annex_clusters/cluster_census.csv')
    pd.testing.assert_frame_equal(census[original.columns].sort_values(['context','cluster_id']).reset_index(drop=True),original.sort_values(['context','cluster_id']).reset_index(drop=True),check_dtype=False)
    assert len(keys)==1007 and len(members)==5346
    assert not keys.duplicated(['context','cluster_id']).any()
    assert not members.duplicated(['context','public_compound_id']).any()
    assert np.array_equal(keys.centroid_row,np.arange(len(keys)))
    assert np.array_equal(members.groupby('atlas_id').size().reindex(keys.atlas_id),keys.n_members)
    P=np.load(atlas/'program_centroids.npy',allow_pickle=False)
    G=np.load(atlas/'gene_centroids.npy',allow_pickle=False)
    assert P.shape==(1007,32) and G.shape==(1007,6000)
    all_recipes=set(pd.read_parquet(package/'core/recipes.parquet',columns=['public_compound_id']).public_compound_id)
    assert set(members.public_compound_id)<=all_recipes
    max_p=max_g=max_coh=0.0
    for context,groups in keys.groupby('context',sort=True):
        uk=pd.read_parquet(package/'core/usages'/f'usages_{context}_compounds.parquet',columns=['public_compound_id'])
        sk=pd.read_parquet(package/'core/surfaces'/f'{context}_compounds.parquet',columns=['public_compound_id'])
        U=np.load(package/'core/usages'/f'usages_{context}.npy',mmap_mode='r',allow_pickle=False)
        S=np.load(package/'core/surfaces'/f'surfaces_{context}.npy',mmap_mode='r',allow_pickle=False)
        ui=pd.Series(np.arange(len(uk)),index=uk.public_compound_id)
        si=pd.Series(np.arange(len(sk)),index=sk.public_compound_id)
        contextual=members[members.context.eq(context)]
        for row in groups.itertuples():
            m=contextual[contextual.cluster_id.eq(row.cluster_id)].sort_values('member_order')
            assert np.array_equal(m.member_order,np.arange(row.n_members))
            ur=ui.loc[m.public_compound_id].to_numpy();sr=si.loc[m.public_compound_id].to_numpy()
            assert np.array_equal(ur,m.core_usage_row) and np.array_equal(sr,m.core_surface_row)
            u=np.asarray(U[ur],dtype='float64')
            p=np.median(u,axis=0).astype('float32')
            g=np.asarray(S[sr].mean(axis=0),dtype='float32')
            pe=float(np.max(np.abs(p-P[row.centroid_row])));ge=float(np.max(np.abs(g-G[row.centroid_row])))
            max_p=max(max_p,pe);max_g=max(max_g,ge)
            assert np.allclose(p,P[row.centroid_row],rtol=1e-6,atol=1e-6)
            assert np.allclose(g,G[row.centroid_row],rtol=1e-6,atol=1e-6)
            norms=np.linalg.norm(u,axis=1,keepdims=True);norms[norms==0]=1
            un=u/norms;similarity=un@un.T
            coherence=float(similarity[np.triu_indices(len(m),1)].mean())
            expected=float(census.loc[census.atlas_id.eq(row.atlas_id),'coherence'].iloc[0])
            ce=abs(coherence-expected);max_coh=max(max_coh,ce)
            assert ce<1e-7
        print(f'{context}: {len(groups)} clusters verified',flush=True)
    print(json.dumps({'status':'pass','clusters':len(keys),'memberships':len(members),'max_program_error':max_p,'max_gene_error':max_g,'max_coherence_error':max_coh},indent=2))

if __name__=='__main__':main()
