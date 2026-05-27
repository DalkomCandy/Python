"""
쿼리 저장소 — 트리 구조 JSON 기반 영속성 관리

저장 형식:
[
  {
    "id":       "uuid4",
    "type":     "folder",
    "name":     "평가",
    "children": [
      {"id": "uuid4", "type": "query", "name": "NAV.sql",
       "content": "SELECT ...", "added_at": "YYYY-MM-DD HH:MM:SS"}
    ]
  },
  {"id": "uuid4", "type": "query", "name": "misc.sql", "content": "...", "added_at": "..."}
]
"""

import json
import uuid
from pathlib import Path
from typing  import List, Dict, Optional, Tuple

from utils.formats import fmt_now

TYPE_FOLDER = 'folder'
TYPE_QUERY  = 'query'


def _normalize(item: Dict) -> Dict:
    """
    구버전 데이터 마이그레이션.

    - 'type' 키 없으면 'query'로 기본 설정
    - 'id' 키 없으면 신규 UUID 발급
    - 폴더면 'children' 보장
    """
    if 'id' not in item:
        item['id'] = str(uuid.uuid4())

    # type 키 없으면 content 유무로 추정
    if 'type' not in item:
        item['type'] = TYPE_FOLDER if 'children' in item else TYPE_QUERY

    if item['type'] == TYPE_FOLDER:
        item.setdefault('children', [])
        item['children'] = [_normalize(c) for c in item['children']]
    else:
        item.setdefault('content',  '')
        item.setdefault('added_at', fmt_now())

    return item


class QueryStore:
    """트리 구조 쿼리 목록 영속성 관리"""

    def __init__(self, path: Path):
        self._path = path
        self._data: List[Dict] = []
        self._load()

    # ── IO ───────────────────────────────────────────

    def _load(self):
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding='utf-8'))
            data = raw if isinstance(raw, list) else []
            # 구버전 포맷 자동 마이그레이션
            self._data = [_normalize(item) for item in data]
            # 마이그레이션 후 저장 (다음 로드엔 깨끗하게)
            self._save()
        except Exception:
            self._data = []

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    # ── 내부 탐색 ────────────────────────────────────

    def _find(self, items: List[Dict], qid: str
              ) -> Optional[Tuple[Dict, List[Dict], int]]:
        for i, item in enumerate(items):
            if item.get('id') == qid:
                return item, items, i
            if item.get('type') == TYPE_FOLDER:
                result = self._find(item.get('children', []), qid)
                if result:
                    return result
        return None

    # ── 공개 API ─────────────────────────────────────

    def all(self) -> List[Dict]:
        return list(self._data)

    def get(self, qid: str) -> Optional[Dict]:
        result = self._find(self._data, qid)
        return result[0] if result else None

    def add_query(self, name: str, content: str,
                  parent_id: Optional[str] = None) -> Dict:
        q = {
            'id':       str(uuid.uuid4()),
            'type':     TYPE_QUERY,
            'name':     name,
            'content':  content,
            'added_at': fmt_now(),
        }
        if parent_id:
            result = self._find(self._data, parent_id)
            if result and result[0].get('type') == TYPE_FOLDER:
                result[0].setdefault('children', []).append(q)
            else:
                self._data.append(q)
        else:
            self._data.append(q)
        self._save()
        return q

    def add_folder(self, name: str,
                   parent_id: Optional[str] = None) -> Dict:
        folder = {
            'id':       str(uuid.uuid4()),
            'type':     TYPE_FOLDER,
            'name':     name,
            'children': [],
        }
        if parent_id:
            result = self._find(self._data, parent_id)
            if result and result[0].get('type') == TYPE_FOLDER:
                result[0]['children'].append(folder)
            else:
                self._data.append(folder)
        else:
            self._data.append(folder)
        self._save()
        return folder

    def update(self, qid: str, name: Optional[str] = None,
               content: Optional[str] = None):
        result = self._find(self._data, qid)
        if result:
            item = result[0]
            if name    is not None: item['name']    = name
            if content is not None: item['content'] = content
            self._save()

    def delete(self, qid: str):
        result = self._find(self._data, qid)
        if result:
            _, parent_list, idx = result
            parent_list.pop(idx)
            self._save()

    def move(self, qid: str, new_parent_id: Optional[str] = None):
        result = self._find(self._data, qid)
        if not result:
            return
        item, parent_list, idx = result

        if new_parent_id:
            if self._find([item], new_parent_id):
                return  # 자기 자신 하위로 이동 방지

        parent_list.pop(idx)

        if new_parent_id:
            target = self._find(self._data, new_parent_id)
            if target and target[0].get('type') == TYPE_FOLDER:
                target[0].setdefault('children', []).append(item)
            else:
                self._data.append(item)
        else:
            self._data.append(item)

        self._save()

    def folders(self) -> List[Dict]:
        """전체 폴더 목록 반환 (이동 다이얼로그용)"""
        def _collect(items: List[Dict]) -> List[Dict]:
            result = []
            for item in items:
                if item.get('type') == TYPE_FOLDER:
                    result.append(item)
                    result.extend(_collect(item.get('children', [])))
            return result
        return _collect(self._data)
