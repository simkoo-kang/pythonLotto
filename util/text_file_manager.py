import os
import re
from util.log_util import LogUtil

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from util.list_util import ListUtil


class Node:
    def __init__(self, name: str):
        self._name: str = name
    
    def get_name(self):
        return self._name
    
    def get_start_tag(self):
        return f"<{self._name}>"
    
    def get_end_tag(self):
        return f"</{self._name}>"
    
    def count(self):
        return 0
    
    def to_string(self, tab: str="\t"):
        pass
    
    
class Field(Node):
    def __init__(self, name: str="field", attrs: Dict[str, str]=None, content: str=None):
        """<field> 엘리먼트를 담는 클래스"""
        super().__init__(name=name)
        
        # 생성자에서 처음에 None 또는 빈 딕셔너리로 타입을 확실히 명시해 둡니다.
        self._attrs: Optional[Dict[str, str]] = attrs
        self._content = content

    def get_attr_value(self, attr_name: str=None):
        if not self._attrs or len(self._attrs) < 1 or not attr_name:
            return None
        if attr_name in self._attrs:
            return self._attrs[attr_name]
        return None

    def add_attr(self, name: str, value: str):
        if self._attrs == None:
            self._attrs = {}
        self._attrs[name.strip()] = str(value).strip()
    
    def remove_attr(self, name: str):
        if self._attrs and name in self._attrs:
            del(self._attrs[name])

    def get_attrs(self):
        return self._attrs
    
    def set_attrs(self, attrs: Dict[str, str]=None):
        self._attrs = attrs
    
    def set_content(self, content: str):
        self._content = content.strip()
    
    def get_content(self):
        return self._content
    
    def attrs_count(self):
        if self._attrs:
            return len(self._attrs)
        return 0
    
    def get_start_tag(self):
        sb = ListUtil.StrBuilder(f"<{self._name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(">")
        return sb.to_string("")
    
    def to_string(self) -> str:
        sb = ListUtil.StrBuilder()
        sb.append(self.get_start_tag())
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        sb.append(">")
        if self._content:
            sb.append(self._content)
        sb.append(self.get_end_tag())
        return sb.to_string("")


class Fields(Node):
    def __init__(self, name: str, attrs: Dict[str, str]=None, fields: List[Field]=[]):
        super().__init__(name)
        
        self._attrs: Optional[Dict[str, str]] = attrs
        self._fields: List[Field] = fields
    
    def get_field_by_tag(self, tag: str) -> Field:
        if not self._fields or len(self._fields) < 1:
            return None
        
        return next((f for f in self._fields if f.get_name() == tag), None)
    
    def get_field_by_value(self, value: str) -> Field:
        if not self._fields or len(self._fields) < 1:
            return None
        
        return next((f for f in self._fields if f.get_content() == value), None)

    def add_field(self, fld: Field):
        self._fields.append(fld)
    
    def remove_field(self, fld: Field=None, value: str=None):
        if fld:
            if fld in self._fields:
                self._fields.remove(fld)
                return True
        elif value:
            new_fld: List[Field] = [f for f in self._fields if f.get_content() != value]
            if len(new_fld) == len(self._fields):
                return False
            self._fields = new_fld
            return True
        
        return False
    
    def get_attrs(self):
        return self._attrs
    
    def set_attrs(self, attrs: Dict[str, str]=None):
        self._attrs = attrs
    
    def get_fields(self):
        return self._fields
    
    def set_fields(self, fields: List[Field]=[]):
        self._fields = fields
    
    def attrs_count(self):
        if self._attrs:
            return len(self._attrs)
        return 0
    
    def fields_count(self):
        if self._fields:
            return len(self._fields)
        return 0
    
    def get_start_tag(self):
        sb = ListUtil.StrBuilder(f"<{self._name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(">")
        return sb.to_string("")
    
    def to_string(self) -> str:
        sb = ListUtil.StrBuilder()
        sb.append(self.get_start_tag())
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        sb.append(">")
        if self._fields:
            for fld in self._fields:
                sb.append(fld.to_string())
        
        sb.append(self.get_end_tag())
        return sb.to_string("")


class Head(Fields):
    def __init__(self, name: str="head", attrs: Dict[str, str] = None, fields: List[Field] = []):
        super().__init__(name, attrs, fields)
    
    
class Item(Fields):
    def __init__(self, name: str="item", attrs: Dict[str, str] = None, fields: List[Field] = []):
        super().__init__(name, attrs, fields)


class Items(Node):
    def __init__(self, name: str="items"):
        super().__init__(name)
        
        self._attrs: Optional[Dict[str, str]] = None
        self._head: Optional[Head] = None
        self._items: list[Item] = []
    
    def get_titles(self) -> list[str]:
        titles = []
        for item in self._items:
            titles.append(item.get_field_by_tag("title").get_content().strip())
        return titles
    
    def get_paths(self) -> list[str]:
        paths = []
        for item in self._items:
            paths.append(item.get_field_by_tag("path").get_content().strip())
        return paths
    
    def save(self, file_path: str):
        """_summary/>
        현재 정보를 다시 xml 파일로 저장
        Args:
            file_path (str): 저장할 파일 path
        """
        import xml.etree.ElementTree as ET
        
        # 1. 루트 엘리먼트 생성 (Node 클래스로부터 상속받은 _name 속성 활용)
        root_name = getattr(self, "_name", "items")
        root = ET.Element(root_name)
        
        # 2. 루트의 속성(_attrs) 세팅
        if self._attrs:
            for key, value in self._attrs.items():
                root.set(key, str(value))
                
        # 3. _head 정보 저장 (Head 역시 Fields를 상속받으므로 공통 구조 사용)
        if self._head:
            head_el = ET.SubElement(root, getattr(self._head, "_name", "head"))
            # head의 속성 세팅
            if self._head.get_attrs():
                for key, value in self._head.get_attrs().items():
                    head_el.set(key, str(value))
            # head 내부의 모든 field들을 순회하며 태그로 생성
            if self._head.get_fields():
                for fld in self._head.get_fields():
                    fld_el = ET.SubElement(head_el, fld.get_name())
                    fld_el.text = fld.get_content().strip() if fld.get_content() else ""

        # 4. _items 리스트 순회하며 저장
        for item in self._items:
            item_name = getattr(item, "_name", "item")
            item_el = ET.SubElement(root, item_name)
            
            # item의 속성 세팅
            if item.get_attrs():
                for key, value in item.get_attrs().items():
                    item_el.set(key, str(value))
                    
            # item 내부의 모든 field들을 동적으로 가져와 태그로 생성 (title, path 등 전체 포함)
            if item.get_fields():
                for fld in item.get_fields():
                    fld_el = ET.SubElement(item_el, fld.get_name())
                    fld_el.text = fld.get_content().strip() if fld.get_content() else ""
                    
        # 5. 파일 쓰기 및 예쁜 들여쓰기(Indent) 적용
        tree = ET.ElementTree(root)
        
        # Python 3.9 이상 자동 줄바꿈 및 들여쓰기 처리
        if hasattr(ET, "indent"):
            ET.indent(tree, space="    ", level=0)
            
        with open(file_path, "wb") as f:
            tree.write(f, encoding="utf-8", xml_declaration=True)
    
    @classmethod
    def from_xml(cls, xml_string: str) -> "Item":
        """XML 문자열을 파싱하여 Item 객체를 생성하는 팩토리 메서드"""
        root = ET.fromstring(xml_string)

        # 1. item 태그의 속성(attrs) 파싱
        all_attrs = root.attrib.copy()

        # 2. 하위 <field> 엘리먼트들 파싱
        fields = []
        for field_node in root.findall("field"):
            title = field_node.get("title", "")

            # 문자열 'True', 'true' 등을 불리언 값으로 안전하게 변환
            req_attr = field_node.get("required", "False").lower()
            is_required = req_attr == "true"

            content = field_node.text.strip() if field_node.text else ""

            fields.append(
                Field(name=title, is_required=is_required, content=content)
            )

        return cls(item_id=item_id, attrs=all_attrs, fields=fields)

    def to_string(self) -> str:
        """객체 데이터를 다시 XML 구조의 문자열로 직렬화"""
        # 루트 엘리먼트 생성 및 속성 설정
        root = ET.Element("item", id=self.item_id, **self.attrs)

        # 하위 필드 추가
        for f in self.fields:
            field_attrs = {
                "title": f._name,
                "required": str(f.is_required),  # 부모에서 변수명은 is_required지만 XML 속성은 required로 매핑
            }
            field_node = ET.SubElement(root, "field", **field_attrs)
            field_node.text = f._content

        # 문자열로 변환 (역슬래시 등 깨짐 방지를 위해 인코딩 후 디코딩)
        return ET.tostring(root, encoding="utf-8").decode("utf-8")


class TextManager:

    def __init__(self, file_path, root_name="root", item_name="item", key_name="title"):
        """_summary_
        특정 포멧으로 텍스트 파일 관리
        Args:
            file_path (str): full filename
            root_name (str, "root"): root name
            item_name (str, "entry"): record name
            key_name (str, "title"): 비교하거나 삭제 등에 필요
        """
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.file_path = file_path
        
        self.root_name = root_name
        self.item_name = item_name
        self.key_name = key_name
        
        self.heads = []
        self.items = self.load()
        
        self.updated = False

    def load(self):
        """파일을 읽어서 딕셔너리 리스트로 변환합니다."""
        if not os.path.exists(self.file_path):
            self.logger.debug(f"{self.file_path} 파일이 존재하지 않습니다.")
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()

        heads = re.findall(rf"<head>(.*?)</head>", content, re.DOTALL)
        if heads and 0 < len(heads):
            self.heads = list(heads[0])
        
        # <entry> ... </entry> 블록들을 모두 찾습니다.
        items = re.findall(rf"<{self.item_name}>(.*?)</{self.item_name}>", content, re.DOTALL)

        data_list = []
        for item in items:
            # <태그>내용</태그> 패턴을 추출합니다. (오타 </decription> 등도 허용하도록 유연하게 매칭)
            tags = re.findall(
                r"<(\w+)>(.*?)</\s*\w+\s*>", item, re.DOTALL
            )  # 태그명과 내용을 추출

            item_data = {}
            for tag_name, tag_content in tags:
                item_data[tag_name] = tag_content.strip()

            if item_data:
                data_list.append(item_data)

        return data_list

    def save(self, data_list=None):
        """딕셔너리 리스트를 지정을 한 형식의 텍스트 파일로 저장합니다."""
        if not self.updated:
            if data_list:
                self.updated = True
                self.items = data_list
                self.save()
            return
        
        lines = [f"<{self.root_name}>"]

        for item in self.items:
            lines.append(f"\t<{self.item_name}>")
            for key, value in item.items():
                # 질문 주신 형식(설명 태그 닫을 때 </decription> 오타 반영 또는 일반 닫기 적용 가능)
                # 안전하게 표준 방식으로 닫도록 구현하되, 원하는 형태로 커스텀 가능합니다.
                lines.append(f"\t\t<{key}> {value} </{key}>")
            lines.append(f"\t</{self.item_name}>")

        lines.append(f"</{self.root_name}>")

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    
    def has_key(self, key_value) -> bool:
        """item에 key필드의 값이 key_value인 item이 있는 지 확인"""
        for item in self.items:
            if item[self.key_name] == key_value:
                return True
        return False
    
    def remove_item(self, key_value) -> bool:
        original_count = len(self.items)
        filtered_list = [item for item in self.items if item.get(self.key_name) != key_value]
        if len(filtered_list) == original_count:
            return False
        
        self.items = filtered_list
        self.updated = True
        return True
    
    def add_item(self, new_item):
        """새로운 entry(딕셔너리)를 추가하고 저장합니다."""
        
        # 중복 확인 - 중복이면 먼저 지운다
        key_value = new_item.get(self.key_name)
        if key_value:
            self.remove_item(key_value=key_value)
        
        self.items.append(new_item)
        self.updated = True


# ==========================================
# 사용 예시 (Ctrl + F5로 테스트 가능)
# ==========================================
if __name__ == "__main__":
    # # 1. 파일 경로 지정 (현재 폴더에 test_db.txt 생성)
    # db = TextManager("test_db.txt")

    # # 2. 저장할 임의의 샘플 데이터
    # # sample_data = [
    # #     {"title": "로또 번호 생성기", "description": "이번 주 추천 번호 저장용"},
    # #     {"title": "영화 플레이어 리스트", "description": "최근 시청한 MP4 파일 목록"},
    # # ]
    # db.add_item({"title": "동영상 리스트", "description": "최근 시청한 동영상 파일 목록"})

    # # 3. 파일 쓰기 테스트
    # # print("--- 데이터 저장 중 ---")
    # # db.save(sample_data)
    # db.save()

    # # 4. 파일 읽기 테스트
    # print("--- 데이터 불러오기 결과 ---")
    # loaded_data = db.load()
    # for index, item in enumerate(loaded_data, 1):
    #     print(f"[{index}] 제목: {item.get('title')} | 설명: {item.get('description')}")

    # # 1. 파싱 (XML -> Object)
    # item_obj = Item.from_xml(xml_data)

    # print("--- [1] 파싱된 객체 데이터 내부 확인 ---")
    # print(f"Item ID: {item_obj.item_id}")
    # print(f"기타 속성(Attrs): {item_obj.attrs}")
    # print(f"하위 필드 목록: {item_obj.fields}\n")

    # # 2. 직렬화 (Object -> String)
    # output_xml = item_obj.to_string()

    # print("--- [2] to_string() 변환 결과 ---")
    # print(output_xml)
    
    head = Head()
    
    field = Field()
    field.add_attr("name", "title")
    field.add_attr("key", True)
    field.add_attr("required", True)
    head.add_field(field)

    field = Field()
    field.add_attr("name", "path")
    field.add_attr("key", False)
    field.add_attr("required", True)
    head.add_field(field)

    field = Field()
    field.add_attr("name", "loop")
    field.add_attr("key", False)
    field.add_attr("required", False)
    head.add_field(field)
    
    print(head.to_string())

    print(f"{field.get_attr_value("title")}, {field.get_attr_value("name")}")

    def from_xml(xml_string: str):
        """XML 문자열을 파싱하여 Item 객체를 생성하는 팩토리 메서드"""
        root = ET.fromstring(xml_string)

        # 1. item 태그의 속성(attrs) 파싱
        all_attrs = root.attrib.copy()

        # 2. 하위 <field> 엘리먼트들 파싱
        fields = []
        for field_node in root.findall("field"):
            title = field_node.get("title", "")

            # 문자열 'True', 'true' 등을 불리언 값으로 안전하게 변환
            req_attr = field_node.get("required", "False").lower()
            is_required = req_attr == "true"

            content = field_node.text.strip() if field_node.text else ""

            fields.append(
                Field(name=title, is_required=is_required, content=content)
            )

        return None
    
    
    # 테스트용 XML 데이터
    xml_data = """
    <data id='root'>
        <head id='head' desc='file head information'>
            <field title='title' required='True'></field>
            <field title='path' required='True'></field>
            <field title='loop' required='False'></field>
        </head>
        <items id='items' desc='item list'>
            <item>
                <title> test.mkv </title>
                <path> D:/Workspace/vscode/lotto/videos/movies/test.mkv </path>
                <loop> False </loop>
            </item>
            <item>
                <title> wonderful.mkv </title>
                <path> D:/Workspace/vscode/lotto/videos/movies/wonderful.mkv </path>
                <loop> False </loop>
            </item>
        </items>
    </data>
    """
    
    print("\n\n")
    root = ET.fromstring(xml_data)

    # class ETree:
    #     def __init__(self, root: ET.Element):
    #         self.root = root
        
    #     def __repr__(self):
    #         print(ET.tostring(self.root, encoding="utf-8", xml_declaration=True).decode("utf-8"))


    # etree = ETree(root=root)
    # print(etree.__repr__())

    # # 5. 파일 쓰기 및 예쁜 들여쓰기(Indent) 적용
    # tree = ET.ElementTree(root)
    
    # # Python 3.9 이상 자동 줄바꿈 및 들여쓰기 처리
    # if hasattr(ET, "indent"):
    #     ET.indent(tree, space="    ", level=0)
        
    # with open("test.plx", "wb") as f:
    #     tree.write(f, encoding="utf-8", xml_declaration=True)
    
    data = {"head": [], "items": []}
    item: Item = None
    for it in root.iter():
        print(it.tag, str(it.text).strip())
        match it.tag:
            case "data" | "head" | "items":
                pass
            case "field":
                field = Field()
                for key, value in it.items():
                    field.add_attr(key, value)
                data["head"].append(field)
            case "item":
                item = Item()
                data["items"].append(item)
            case _:
                field = Field(it.tag)
                for key, value in it.items():
                    field.add_attr(key, value)
                field.set_content(it.tag.strip())
                if item:
                    item.add_field(field)
    
    print(data)
    print(len(data['head']), len(data['items']))
    
    # head = root.find("head")
    # print(head.items())
    
    # # 1. item 태그의 속성(attrs) 파싱
    # all_attrs = root.attrib.copy()
    # print(all_attrs)
    