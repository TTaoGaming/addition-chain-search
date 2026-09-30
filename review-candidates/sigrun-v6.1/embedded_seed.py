"""Deterministic inline-content checks independent of network/source file access."""
import hashlib,re

def validate_embedded(text, expected):
    ports = expected['view_order']
    assert ports == ['P'+str(i) for i in range(8)]
    headings = re.findall(r'^# (P[0-7]) [^\n]+$', text, re.M)
    assert headings == ports, ('inline view order/uniqueness', headings)
    for item in expected['views']:
        port=item['port']
        begin='<!-- BEGIN_VIEW '+port+' -->\n'
        end='<!-- END_VIEW '+port+' -->'
        assert text.count(begin)==1 and text.count(end)==1, port
        content=text.split(begin,1)[1].split(end,1)[0]
        assert content.startswith(item['heading']+'\n'), port
        assert content.split('\n',1)[1].strip(), ('empty view',port)
        assert len(content.encode())==item['bytes'], port
        assert hashlib.sha256(content.encode()).hexdigest()==item['sha256'], port
    begin='<!-- BEGIN_CORE_SEED -->\n```text\n'
    end='```\n<!-- END_CORE_SEED -->'
    assert text.count(begin)==1 and text.count(end)==1
    core=text.split(begin,1)[1].split(end,1)[0]
    assert hashlib.sha256(core.encode()).hexdigest()==expected['core_seed_sha256']
    begin='<!-- BEGIN_COMPANION_CONTEXT -->\n'
    end='<!-- END_COMPANION_CONTEXT -->'
    assert text.count(begin)==1 and text.count(end)==1
    context=text.split(begin,1)[1].split(end,1)[0]
    assert hashlib.sha256(context.encode()).hexdigest()==expected['companion_context_sha256']
    for required in ['Current technology and recovery map','Slack','GitHub','Cloudflare','Evolution']:
        assert required in context, required
    return {'inline_views':'PASS','ports':ports,'core_seed':'PASS','technology_map':'PASS','external_fetch_for_core_content':False}
