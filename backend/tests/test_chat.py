import json

from app.services.rag.answer import NO_EVIDENCE, answer_question


def test_chat_requires_server_key_and_rejects_bad_request(context):
    client = context['client']
    assert client.post('/api/v1/chat', json={'question': 'Bàu Dũ là gì?'}).status_code == 503
    context['settings'].gemini_api_key = 'test-key'
    assert client.post('/api/v1/chat', json={'question': 'a'}).status_code == 422
    assert client.post('/api/v1/chat', json={'question': 'Bàu Dũ là gì?', 'topic_id': 'bad'}).status_code == 422
    response = client.post('/api/v1/chat', json={'question': 'Bàu Dũ là gì?', 'topic_id': 'TOPIC001'})
    assert response.status_code == 200
    assert response.json() == {'answer': NO_EVIDENCE, 'answered': False, 'sources': []}


def test_answer_uses_only_verified_chunks_and_returns_backend_sources(tmp_path):
    processed = tmp_path / 'processed'
    processed.mkdir()
    (processed / 'chunks.json').write_text(json.dumps([
        {'chunk_id': 'DOC1_v1_001', 'topic_id': 'TOPIC005', 'topic_ids': ['TOPIC005'],
         'title': 'Bàu Dũ', 'text': 'Người cổ sống bằng săn bắt và hái lượm.',
         'source_asset_ids': ['asset-1'], 'source_filenames': ['IMG_8798.JPG'],
         'review_status': 'verified'},
        {'chunk_id': 'DRAFT_v1_001', 'topic_id': 'TOPIC005', 'topic_ids': ['TOPIC005'],
         'title': 'Bản nháp', 'text': 'Thông tin chưa xác minh.',
         'source_asset_ids': ['asset-2'], 'source_filenames': ['DRAFT.JPG'],
         'review_status': 'needs_review'},
    ]))
    prompts = []
    def fake_generate(prompt):
        prompts.append(prompt)
        return 'Người cổ sống bằng săn bắt và hái lượm.'
    result = answer_question('Người cổ sống bằng gì?', 'TOPIC005', tmp_path,
                             'test-key', 'test-model', fake_generate)
    assert result['answered'] is True
    assert result['sources'][0]['chunk_id'] == 'DOC1_v1_001'
    assert result['sources'][0]['image_urls'] == ['/api/v1/assets/asset-1/file']
    assert 'Thông tin chưa xác minh' not in prompts[0]
    assert answer_question('Người cổ sống bằng gì?', 'TOPIC006', tmp_path,
                           'test-key', 'test-model', fake_generate)['answered'] is False
    assert len(prompts) == 1
