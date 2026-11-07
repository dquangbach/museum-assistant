import json
import tempfile
import unittest
from pathlib import Path
from app.services.rag.ingestion import build_chunks, load_documents, split_text, ocr_search_text
from app.services.rag.retrieval import search_chunks
from scripts.ocr_dataset import parse_tsv
from scripts.import_reviewed import validate


def document(**changes):
    row={'document_id':'D','topic_id':'T1','topic_ids':['T1','T2'],'exhibit_id':None,
         'title':'Title','language':'vi','text':'Văn bản thứ nhất.\n\nVăn bản thứ hai.',
         'source_asset_ids':['A'],'source_filenames':['A.JPG'],'version':1,
         'review_status':'verified','review_notes':'Checked against source.'}
    row.update(changes)
    return row


class PipelineTests(unittest.TestCase):
    def test_verified_boundary_and_review_flag(self):
        docs=[document(),document(document_id='D2',review_status='needs_review')]
        self.assertEqual(len(build_chunks(docs)),2)
        self.assertEqual(len(build_chunks(docs,include_drafts=True)),4)
        self.assertEqual(build_chunks(docs)[0]['source_asset_ids'],['A'])

    def test_ocr_noise_grouping_preserves_raw_and_verified(self):
        raw = "x\n\n---\n\nNam Thổ Sơn\n\nthuộc văn hóa Chăm."
        self.assertEqual(ocr_search_text(raw), "Nam Thổ Sơn thuộc văn hóa Chăm.")
        doc = document(text=raw, ocr_status='text_detected', review_status='needs_review')
        self.assertEqual(len(build_chunks([doc],True)),1)
        self.assertEqual(doc['text'],raw)
        self.assertEqual(len(build_chunks([document(text=raw,ocr_status='text_detected')])),4)

    def test_shared_topic_search(self):
        chunks=build_chunks([document()])
        self.assertEqual(len(search_chunks('văn bản',chunks,topic_id='T2')),2)
        self.assertEqual(search_chunks('văn bản',chunks,topic_id='T3'),[])
        self.assertEqual(search_chunks('văn bản',chunks,top_k=0),[])

    def test_unassigned_not_indexed(self):
        self.assertEqual(build_chunks([document(topic_id=None,topic_ids=[])],True),[])

    def test_split_long_text_without_loss(self):
        text=' '.join(['kiến thức']*500)
        pieces=list(split_text(text,100))
        self.assertTrue(all(len(p)<=100 for p in pieces))
        self.assertEqual(' '.join(pieces),text)

    def test_existing_paragraph_ids(self):
        self.assertEqual([c['chunk_id'] for c in build_chunks([document()])],['D_v1_001','D_v1_002'])

    def test_duplicate_documents_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'documents.json';p.write_text(json.dumps([document(),document()]))
            with self.assertRaises(ValueError):load_documents(p)

    def test_ocr_preserves_quoted_words(self):
        tsv='level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
        tsv+='5\t1\t1\t1\t1\t1\t0\t0\t10\t10\t90\t"Sa\n'
        tsv+='5\t1\t1\t1\t1\t2\t10\t0\t10\t10\t80\tHuỳnh"\n'
        text,words=parse_tsv(tsv)
        self.assertEqual(text,'"Sa Huỳnh"');self.assertEqual(len(words),2)

    def test_review_validation(self):
        assets={'A':{'original_filename':'A.JPG'}}
        topics={'T1','T2'};links={('T1','A'),('T2','A')}
        self.assertEqual(validate(document(),assets,topics,links)['document_id'],'D')
        for changes in [{'review_status':'needs_review'},{'language':'und'},
                        {'source_filenames':['other.JPG']},{'topic_id':'unknown'}]:
            with self.assertRaises(ValueError):validate(document(**changes),assets,topics,links)


if __name__=='__main__':unittest.main()
