import os
import re
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

from util.str_util import Str
from util.list_util import ListUtil
from util.file_util import FileUtil
from util.text_file_manager import Field
from util.log_util import LogUtil


class AttrNode:
    def __init__(self, tag_name: str, attrs: Optional[Dict[str, str]]=None):
        """_summary_
        tag name without content
        Args:
            name (str): _description_
            attrs (Optional[Dict[str, str]], None): attrs
        """
        self._tag_name: str = tag_name
        self._attrs: Optional[Dict[str, str]] = attrs
    
    def get_tag_name(self) -> str:
        """_summary_
        get tag name
        Returns:
            str: tag name
        """
        return self._tag_name
    
    def set_tag_name(self, tag_name):
        """_summary_
        set tag name
        Args:
            name (str): tag name
        """
        self._tag_name = tag_name
    
    def get_attr_value(self, attr_name: str) -> str:
        """_summary_
        attr value
        Args:
            attr_name (str): attr name
        Returns:
            str: attr value or None
        """
        if not self._attrs or len(self._attrs) < 1:
            return None
        if attr_name in self._attrs:
            return self._attrs[attr_name]
        return None

    def add_attr(self, attr_name: str, attr_value):
        """_summary_
        append attr
        Args:
            name (str): attr name
            value (variable): attr value
        """
        if self._attrs == None:
            self._attrs = {}
        self._attrs[attr_name.strip()] = str(attr_value).strip()
    
    def remove_attr(self, tag_name: str) -> bool:
        """_summary_
        remove attr with name
        Args:
            name (str): attr name
        """
        if self._attrs and tag_name in self._attrs:
            del(self._attrs[tag_name])
            return True
        return False

    def get_attrs(self) -> Optional[Dict[str, str]]:
        """_summary_
        all attrs
        Returns:
            Optional[Dict[str, str]]: all attrs
        """
        return self._attrs
    
    def set_attrs(self, attrs: Dict[str, str]):
        """_summary_
        attrs at all
        Args:
            attrs (Dict[str, str]): attrs all
        """
        self._attrs = attrs
    
    def get_noncontent_tag(self) -> str:
        """_summary_
        none content tag
        Returns:
            str: <name attrs />
        """
        sb = ListUtil.StrBuilder(f"<{self._tag_name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(" />")
        return sb.to_string("")
    
    def get_start_tag(self) -> str:
        """_summary_
        start tag
        Returns:
            str: <name attrs>
        """
        sb = ListUtil.StrBuilder(f"<{self._tag_name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(">")
        return sb.to_string("")
    
    def get_end_tag(self) -> str:
        """_summary_
        end tag
        Returns:
            str: </name>
        """
        return f"</{self._tag_name}>"
    
    def attr_count(self) -> int:
        """_summary_
        count attrs
        Returns:
            int: count attrs or 0
        """
        if self._attrs is not None:
            return len(self._attrs)
        return 0
    
    def to_string(self) -> str:
        return self.get_noncontent_tag()
    
    
class Field(AttrNode):
    def __init__(self, tag_name: str="field", attrs: Optional[Dict[str, str]]=None, text: str=None):
        """_summary_
        field element class
        Args:
            tag_name (str): tag name
            attrs (Optional[Dict[str, str]], None): attrs
            text (str, None): content
        """
        super().__init__(tag_name, attrs)
        
        # 생성자에서 처음에 None 또는 빈 딕셔너리로 타입을 확실히 명시해 둡니다.
        self._text = text

    def set_text(self, text: str) -> str:
        self._text = text.strip()
    
    def get_text(self) -> str:
        if self._text.strip():
            return self._text
        return ""
    
    def to_string(self) -> str:
        sb = ListUtil.StrBuilder()
        sb.append(self.get_start_tag())
        if not Str.is_blank(self._text):
            sb.append(self._text)
        sb.append(self.get_end_tag())
        return sb.to_string("")


class ItemNode(AttrNode):
    def __init__(self, tag_name: str, attrs: Optional[Dict[str, str]]=None, nodes: List=[]):
        """_summary_
        tag_name, attrs and field list
        Args:
            tag_name (str): tag name
            attrs (Optional[Dict[str, str]], None): attrs
            fields (List[Field], None): child fields
        """
        super().__init__(tag_name, attrs)
        
        self._nodes: List = nodes
    
    def get_node_by_tag(self, tag_name: str):
        """_summary_
        get node with tag name
        Args:
            tag_name (str): tag name
        Returns:
            node: field or item else None
        """
        if not self._nodes or len(self._nodes) < 1:
            return None
        
        return next((node for node in self._nodes if node.get_tag_name() == tag_name), None)
    
    def get_node_by_text(self, text: str):
        """_summary_
        search text and find then return field or item
        Args:
            text (str): content
        Returns:
            Field or Item: field containing text
        """
        if not self._nodes or len(self._nodes) < 1:
            return None
        
        return next((node for node in self._nodes if node.get_text() == text), None)

    def add_field(self, node):
        """_summary_
        append field or item
        Args:
            node (Field, Item): 추가할 필드
        """
        self._nodes.append(node)
    
    def remove_node(self, node=None, text: str=None) -> bool:
        """_summary_
        필드 삭제
        Args:
            node (Field or Item, None): 삭제할 필드
            text (str, None): 삭제할 필드의 text
        Returns:
            bool: True if del else False
        """
        if node:
            if node in self._nodes:
                self._nodes.remove(node)
                return True
        elif text:
            new_flds: List[Field] = [f for f in self._nodes if f.get_text() != text]
            if len(new_flds) == len(self._nodes):
                return False
            self._nodes = new_flds
            return True
        
        return False
    
    def get_nodes(self) -> list:
        """_summary_
        field list
        Returns:
            list[]: 전체 필드
        """
        return self._nodes
    
    def set_fields(self, fields: List=[]):
        self._nodes = fields
    
    def fields_count(self) -> int:
        if self._nodes:
            return len(self._nodes)
        return 0
    
    def to_string(self, tab: str="\t") -> str:
        """_summary_
        전체 데이터 구조화
        Args:
            tab (str, '\t'): 들여 쓰기
        Returns:
            str:
            <item attrs>
                <field attrs> text </field>
                <field attrs> text </field>
            </item>
        """
        sb = ListUtil.StrBuilder(f"{tab}{self.get_start_tag()}")
        if self._nodes and 0 < len(self._nodes):
            for f in self._nodes:
                sb.append(f"\n{tab}\t{f.to_string()}")
            sb.append(f"\n{tab}{self.get_end_tag()}")
            return sb.to_string("")
        return None


class Head(ItemNode):
    def __init__(self, tag_name: str="head", attrs: Optional[Dict[str, str]] = None, fields: List = []):
        super().__init__(tag_name, attrs, fields)
    
    
class Item(ItemNode):
    def __init__(self, tag_name: str="item", attrs: Optional[Dict[str, str]] = None, fields: List = []):
        super().__init__(tag_name, attrs, fields)


class Items(AttrNode):
    def __init__(self, tag_name: str="items", attrs: Optional[Dict[str, str]] = None):
        super().__init__(tag_name, attrs)
        
        self._head: Optional[Head] = None
        self._items: list[Item] = []
    
    def to_string(self, tab: str="\t") -> str:
        """_summary_
        전체 데이터 구조화
        Args:
            tab (str, '\t'): 들여 쓰기
        Returns:
            str:
            <items attrs>
                <item attrs>
                    <field attrs> text </field>
                    <field attrs> text </field>
                </item>
            </items>
        """
        sb = ListUtil.StrBuilder(f"{tab}{self.get_start_tag()}")
        if self._nodes and 0 < len(self._nodes):
            for f in self._nodes:
                sb.append(f"\n{tab}\t{f.to_string()}")
            sb.append(f"\n{tab}{self.get_end_tag()}")
            return sb.to_string("")
        return None

class Data(Field):
    def __init__(self, name = "data", attrs: Optional[Dict[str, str]] = None, file_path: str=None, xml_data: str=None):
        super().__init__(name, attrs)
        
        self._head: Optional[Head] = None
        self._items: list[Item] = []

        self.xml_root: Optional[ET.Element] = None
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.file_path = file_path
        self.xml_data = xml_data
        if self.file_path:
            self.load_from_file(self.file_path)
        elif xml_data:
            self.load_from_string(self.xml_data)
        
        self.updated = False
    
    def add_head_field(self, fld: Field) -> Field:
        self._head.add_field(node=fld)
        self.updated = True
    
    def get_head_field(self, tag: str) -> Field:
        return self._head.get_node_by_tag(tag_name=tag)
    
    def get_item(self, index=-1, value: str=None) -> Item:
        if 0 <= index < len(self._items):
            return self._items[index]
        
        if value is None:
            self.logger.debug(f"입력 정보가 부족합니다. index[{index}]", value=None)
            return None
        
        for item in self._items:
            fld = item.get_node_by_text(text=value)
            if fld:
                return item
        
        self.logger.debug(f"(index, valu)=({index}, {value}) 일치하는 정보가 없습니다.")
        return None
    
    def add_item(self, item: Item):
        self._items.append(item)
        self.updated = True

    def remove_item_first(self):
        del self._items[0]
        self.updated = True

    def remove_item_last(self):
        self._items.pop()
        self.updated = True
    
    def remove_item_index(self, index):
        if 0 <= index < len(self._items):
            del self._items[index]
            self.updated = True
            return True
        return False

    def remove_item_by_tagvalue2(self, tag:str, value: str) -> bool:
        items = [
            item for item in self._items 
            if item.get_node_by_tag(tag).get_text().strip() != value
        ]
        if len(items) == len(self._items):
            return False
        self._items = items
        self.updated = True
        return True

    def remove_item_by_tagvalue(self, tag:str, value: str) -> bool:
        for item in self._items:
            title_fld = item.get_node_by_tag(tag_name=tag)
            if title_fld and title_fld.get_text().strip() == value:
                self._items.remove(item)
                self.updated =True
                return True
        return False
    
    def get_head(self):
        return self._head
    
    def set_head(self, head: Head):
        self._head = head
    
    def get_items(self):
        return self._items
    
    def set_items(self, items: list[Item]):
        self._items = items
    
    def get_info_list(self, tag_name: str):
        infos = []
        for item in self._items:
            infos.append(item.get_node_by_tag(tag_name=tag_name).get_text().strip())
        return infos
    
    def save(self, file_path: str=None):
        """_summary/>
        현재 정보를 다시 xml 파일로 저장
        Args:
            file_path (str): 저장할 파일 path
        """
        if not self.updated:
            self.logger.debug(f"변경된 내용이 없습니다.({file_path})")
            return
        
        save_file = file_path if file_path else self.file_path
        xml_data = self.to_string()
        if save_file is not None and xml_data is not None:
            FileUtil.writeln(file_path=save_file, string=xml_data, mode="w")
    
    def load_from_file(self, file_path):
        import os
        if os.path.exists(file_path):
            xml_string = FileUtil.read_all(self.file_path)
            self.load_from_string(xml_string)
    
    def update_from_data(self):
        xml_string = self._to_string()
        self.load_from_string(xml_string=xml_string)
    
    def load_from_string(self, xml_string):
        self.xml_root = ET.fromstring(xml_string)
        # data = {"head": [], "items": []}
        data = {}
        item: Item = None
        for it in self.xml_root.iter():
            match it.tag:
                case "data":
                    pass
                case "head" | "items":
                    data[it.tag] = []
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
                    field.set_text(it.tag.strip())
                    if item:
                        item.add_field(field)

        self.updated = False
    
    def _to_string(self) -> str:
        sb = ListUtil.StrBuilder("<?xml version='1.0' encoding='utf-8'?>").append(self.get_start_tag())
        
        # 1. 시작 태그 (예: <items>)
        # get_start_tag()가 없다면 기본 문자열 구조로 대체 가능합니다.
        
        # 2. Head 정보가 있다면 문자열에 포함
        if self._head:
            sb.append(self._head.to_string())
            
        # 3. 추가된 Item들을 순회하며 각각의 문자열을 추가 (이 부분이 누락되었었습니다!)
        if self._items:
            for item in self._items:
                sb.append(item.to_string())
                
        # 4. 종료 태그 (예: </items>)
        sb.append(f"</{getattr(self, '_name', 'items')}>")
        
        sb.append(self.get_end_tag())
        return sb.to_string("\n") # 줄바꿈을 주면 알아보기 더 쉽습니다.
    
    def to_string(self) -> str:
        if self.updated:
            self.update_from_data()
        
        if self.xml_root is not None and 0 < len(self.xml_root): 
            # 4. 예쁜 들여쓰기(Indent) 적용
            if hasattr(ET, "indent"):
                ET.indent(self.xml_root, space="    ", level=0)
                
            # 5. [핵심] 문자열(bytes)로 추출 후 디코딩하여 str 반환
            # xml_declaration=True를 주면 <?xml version='1.0' encoding='utf-8'?> 선언문이 포함됩니다.
            xml_bytes = ET.tostring(self.xml_root, encoding="utf-8", xml_declaration=True)
            return xml_bytes.decode("utf-8")
        return None


# ==========================================
# 실행 및 통합 파싱 테스트 (Ctrl + F5)
# ==========================================
if __name__ == "__main__":

    file_path = "test.plx"
    data = Data(file_path=file_path)
    print(data.to_string())
    
    item = Item()
    
    item.add_field(Field("title", content="good.avi"))
    item.add_field(Field("path", content="D:/Workspace/vscde/lotto/videos/movies/good.avi"))
    item.add_field(Field("loop", content="True"))
    data.add_item(item)
    
    data.save(file_path=file_path)
    print(data.to_string())
