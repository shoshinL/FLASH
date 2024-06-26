# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
added_files = [
    ('.\\gui', 'gui'),
]

added_files += collect_data_files('chromadb', include_py_files=True, includes=['**/*.py', '**/*.sql'])

a = Analysis(
    ['.\\backend\\index.py'],
    pathex=['.\\dist'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
    'clr', 'tiktoken_ext.openai_public', 'tiktoken_ext',
    'chromadb',
    'chromadb.api',
    'chromadb.api.client',
    'chromadb.api.fastapi',
    'chromadb.api.segment',
    'chromadb.api.types',
    'chromadb.app',
    'chromadb.auth',
    'chromadb.auth.basic_authn',
    'chromadb.auth.simple_rbac_authz',
    'chromadb.auth.token_authn',
    'chromadb.cli',
    'chromadb.cli.cli',
    'chromadb.cli.utils',
    'chromadb.config',
    'chromadb.db',
    'chromadb.db.base',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'chromadb.db.impl.sqlite_pool',
    'chromadb.db.migrations',
    'chromadb.db.system',
    'chromadb.errors',
    'chromadb.ingest',
    'chromadb.migrations',
    'chromadb.migrations.embeddings_queue',
    'chromadb.proto',
    'chromadb.proto.chroma_pb2',
    'chromadb.proto.chroma_pb2_grpc',
    'chromadb.proto.convert',
    'chromadb.proto.coordinator_pb2',
    'chromadb.proto.coordinator_pb2_grpc',
    'chromadb.proto.logservice_pb2',
    'chromadb.proto.logservice_pb2_grpc',
    'chromadb.quota',
    'chromadb.quota.test_provider',
    'chromadb.rate_limiting',
    'chromadb.rate_limiting.test_provider',
    'chromadb.segment',
    'chromadb.segment.distributed',
    'chromadb.segment.impl',
    'chromadb.segment.impl.manager',
    'chromadb.segment.impl.manager.cache',
    'chromadb.segment.impl.manager.cache.cache',
    'chromadb.segment.impl.manager.distributed',
    'chromadb.segment.impl.manager.local',
    'chromadb.server',
    'chromadb.server.fastapi',
    'chromadb.server.fastapi.types',
    'chromadb.telemetry',
    'chromadb.telemetry.opentelemetry',
    'chromadb.telemetry.opentelemetry.fastapi',
    'chromadb.telemetry.opentelemetry.grpc',
    'chromadb.telemetry.product',
    'chromadb.telemetry.product.events',
    'chromadb.telemetry.product.posthog',
    'chromadb.types',
    'chromadb.utils',
    'chromadb.utils.batch_utils',
    'chromadb.utils.data_loaders',
    'chromadb.utils.delete_file',
    'chromadb.utils.directory',
    'chromadb.utils.distance_functions',
    'chromadb.utils.embedding_functions',
    'chromadb.utils.fastapi',
    'chromadb.utils.lru_cache',
    'chromadb.utils.messageid',
    'chromadb.utils.read_write_lock',
    'chromadb.utils.rendezvous_hash',
    'posthog',
    'numpy',
    'onnxruntime',
    'tokenizers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='FLASH for Anki',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          icon='.\\backend\\assets\\logo.ico',
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
