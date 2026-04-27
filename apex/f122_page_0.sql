prompt --application/set_environment
set define off verify off feedback off
whenever sqlerror exit sql.sqlcode rollback
--------------------------------------------------------------------------------
--
-- Oracle APEX export file
--
-- You should run the script connected to SQL*Plus as the Oracle user
-- APEX_220100 or as the owner (parsing schema) of the application.
--
-- NOTE: Calls to apex_application_install override the defaults below.
--
--------------------------------------------------------------------------------
begin
wwv_flow_imp.import_begin (
 p_version_yyyy_mm_dd=>'2022.04.12'
,p_release=>'22.1.0'
,p_default_workspace_id=>1501145227114753
,p_default_application_id=>122
,p_default_id_offset=>0
,p_default_owner=>'INV'
);
end;
/
 
prompt APPLICATION 122 - Kairos
--
-- Application Export:
--   Application:     122
--   Name:            Kairos
--   Date and Time:   11:03 Monday April 27, 2026
--   Exported By:     NZARATE
--   Flashback:       0
--   Export Type:     Page Export
--   Manifest
--     PAGE: 0
--   Manifest End
--   Version:         22.1.0
--   Instance ID:     69411747885904
--

begin
null;
end;
/
prompt --application/pages/delete_00000
begin
wwv_flow_imp_page.remove_page (p_flow_id=>wwv_flow.g_flow_id, p_page_id=>0);
end;
/
prompt --application/pages/page_00000
begin
wwv_flow_imp_page.create_page(
 p_id=>0
,p_user_interface_id=>wwv_flow_imp.id(40210426655263685)
,p_name=>'Global Page - Desktop'
,p_autocomplete_on_off=>'OFF'
,p_protection_level=>'D'
,p_page_component_map=>'14'
,p_last_updated_by=>'RUBENITEZ'
,p_last_upd_yyyymmddhh24miss=>'20260108160957'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(12525684456514418)
,p_plug_name=>'SearchNavMenu'
,p_region_template_options=>'#DEFAULT#'
,p_region_attributes=>'style="display:none;"'
,p_plug_template=>wwv_flow_imp.id(40096829222263653)
,p_plug_display_sequence=>300
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(40329574666321623)
,p_plug_name=>'R0_ITEMS'
,p_region_template_options=>'#DEFAULT#'
,p_plug_template=>wwv_flow_imp.id(40096829222263653)
,p_plug_display_sequence=>900
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(103903814029744602)
,p_plug_name=>'&nbsp'
,p_region_template_options=>'#DEFAULT#:t-Region--noPadding:t-Region--noUI:t-Region--scrollBody:margin-bottom-none'
,p_plug_template=>wwv_flow_imp.id(40125238939263661)
,p_plug_display_sequence=>990
,p_plug_display_point=>'REGION_POSITION_01'
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_plug_display_condition_type=>'FUNCTION_BODY'
,p_plug_display_when_condition=>wwv_flow_string.join(wwv_flow_t_varchar2(
'DECLARE',
'VEXISTE NUMBER;',
'BEGIN',
'    SELECT 1',
'      INTO VEXISTE',
'      FROM ASP$MODU0300',
'     WHERE DM$ACTI = 1',
'       AND APLI0100$ID = :P_APLI0100_ID',
'       AND PAGE_ID = :APP_PAGE_ID',
'       AND ROWNUM = 1;',
'',
'',
'',
'',
'    RETURN FALSE;',
' ',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        RETURN FALSE;',
'END;'))
,p_plug_display_when_cond2=>'PLSQL'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(104444646536494202)
,p_plug_name=>'Ruta de Navegacion'
,p_region_template_options=>'#DEFAULT#:t-BreadcrumbRegion--compactTitle:t-BreadcrumbRegion--useBreadcrumbTitle'
,p_component_template_options=>'#DEFAULT#'
,p_plug_template=>wwv_flow_imp.id(40134615190263663)
,p_plug_display_sequence=>1000
,p_plug_display_point=>'REGION_POSITION_01'
,p_menu_id=>wwv_flow_imp.id(40070279985263645)
,p_plug_source_type=>'NATIVE_BREADCRUMB'
,p_menu_template_id=>wwv_flow_imp.id(40189153869263678)
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_plug_display_condition_type=>'FUNCTION_BODY'
,p_plug_display_when_condition=>wwv_flow_string.join(wwv_flow_t_varchar2(
'DECLARE',
'VEXISTE NUMBER;',
'VPAGE   VARCHAR2(15);',
'BEGIN',
'    SELECT 1',
'      INTO VEXISTE',
'      FROM ASP$MODU0300',
'     WHERE DM$ACTI = 1',
'       AND APLI0100$ID = :P_APLI0100_ID',
'       AND PAGE_ID = :APP_PAGE_ID',
'       AND ROWNUM = 1;',
'  BEGIN  ',
'  select PAGE_MODE',
'    INTO VPAGE',
'    from APEX_220100.APEX_APPLICATION_PAGES',
'   where workspace  = (SELECT S.workspace FROM APEX_220100.APEX_APPLICATIONS S WHERE S.application_id = :APP_ID) ',
'     and page_id = :APP_PAGE_ID',
'     and application_id = :APP_ID',
'     and page_id not in (1,146,99999)',
'     and page_mode = ''Normal'';',
'    EXCEPTION WHEN OTHERS THEN ',
'      RETURN FALSE;',
'  END;',
'',
'    RETURN true;',
' ',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        RETURN false;',
'END;'))
,p_plug_display_when_cond2=>'PLSQL'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(159646111738341730)
,p_plug_name=>unistr('Imagenes Men\00FA')
,p_region_template_options=>'#DEFAULT#'
,p_plug_template=>wwv_flow_imp.id(40096829222263653)
,p_plug_display_sequence=>1010
,p_include_in_reg_disp_sel_yn=>'Y'
,p_plug_display_point=>'REGION_POSITION_05'
,p_plug_source=>wwv_flow_string.join(wwv_flow_t_varchar2(
'<div style="display:inline-flex; width:100%;">',
'    <div style="width:50%;">',
'        <img src="#APP_FILES#logo-ngo.png"/ style="width:100px;  opacity: 90%;">',
'    </div>',
'    <div style="margin-left:40%;">',
'        <img src="#APP_FILES#fondoN-removebg-preview.png"/ style="width:150px;  opacity: 90%;">',
'    </div>',
'</div>',
'',
'',
''))
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_plug_display_condition_type=>'CURRENT_PAGE_IN_CONDITION'
,p_plug_display_when_condition=>'1,385,389,390,391'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(188180867684669318)
,p_plug_name=>'Llamador reportes'
,p_region_template_options=>'#DEFAULT#'
,p_plug_template=>wwv_flow_imp.id(40096829222263653)
,p_plug_display_sequence=>930
,p_plug_source=>wwv_flow_string.join(wwv_flow_t_varchar2(
'<script  type="text/javascript">',
'',
'// 1- FUNCION QUE LLAMA A LOS REPORTES JASPER',
'const createReportUrl = (reportName, parametros) => {',
'      const params = parametros',
'   ',
'      for(let input of $(''.report-input'')) {',
'            const id = $(input).attr(''id'')',
'       ',
'        const value = $v(id) + ''''',
'            params.push({',
'                  name: id.replace(''P&APP_PAGE_ID._'', ''''),',
'                  value',
'            })',
'      }',
'  ',
'      const paramsUrl = params.map(({name,value}) => `${name}=${value}`).join(''&'')',
'',
'      const url = `&REPORT_BASE_URL_TEST.${reportName}&standAlone=true&j_username=&REPORT_USER.&j_password=&REPORT_PASS.&output=&REPORT_FORMAT.&${paramsUrl}`',
'',
'      apex.server.process(''SET_REPORT_URL'', {',
'        x01: url',
'      }).then(data =>',
'								',
'            window.open(data)',
'            //apex.navigation.redirect(data)',
'      ).catch(err =>',
'            console.log(err)',
'      )',
'				 ',
'}',
'',
unistr('//Funci\00F3n para realizar la impresi\00F3n de manera directa del Jasper sin descarga local ni especificar orientaci\00F3n '),
'function Jasper_impresion_directa(reporte, parametros){ ',
'    var spinner = apex.util.showSpinner(); ',
'    $("#apex_wait_overlay").remove(); ',
'    var parametrosURL = parametros.map(({name,value}) => `${name}=${value}`).join(''&''); ',
'    var url = `&REPORT_BASE_URL.${reporte}&standAlone=true&j_username=&REPORT_USER.&j_password=&REPORT_PASS.&output=&REPORT_FORMAT.&${parametrosURL}` ',
'    console.log(url); ',
'    var req = new XMLHttpRequest(); ',
'    req.open(''GET'',url,true); ',
'    req.withCredentials = false; ',
'    req.responseType = "blob"; ',
'    req.onload = function(event){ ',
'        var reporte = req.response; ',
'        var datos = new FormData(); ',
'        datos.append("archivo", reporte); ',
'        var xhr = new XMLHttpRequest(); ',
'        xhr.withCredentials = false; ',
'        xhr.open("POST","http://localhost:28080/api/imprimirpost"); ',
'        xhr.onreadystatechange = function(event){ ',
'            if(xhr.status != 200){ ',
'                apex.message.clearErrors();',
unistr('                apex.message.showErrors([{type: "error", message: "No se encuentra en ejecuci\00F3n o actualizado el servicio de impresi\00F3n...", location: "page", unsafe: false}]); '),
'                $(".u-Processing").remove(); ',
'            } ',
'        } ',
'        xhr.onload = function(event){ ',
'            var retorno = xhr.response; ',
'            if(retorno == ''true''){ ',
unistr('                apex.message.showPageSuccess("El archivo fue impreso con \00E9xito!"); '),
'                $(".u-Processing").remove(); ',
'            }else{ ',
'                apex.message.clearErrors(); ',
'                apex.message.showErrors([{type: "error", message: "Hubo un error al imprimir...", location: "page", unsafe: false}]); ',
'                $(".u-Processing").remove(); ',
'            } ',
'        } ',
'        xhr.send(datos); ',
'    } ',
'    req.send(); ',
'} ',
'',
'',
'',
'',
'',
'',
'</script>'))
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(250693843151243206)
,p_plug_name=>'Parametros para notificacion'
,p_region_template_options=>'#DEFAULT#'
,p_region_attributes=>'style="display:none"'
,p_plug_template=>wwv_flow_imp.id(40096829222263653)
,p_plug_display_sequence=>920
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_button(
 p_id=>wwv_flow_imp.id(103903911751744603)
,p_button_sequence=>10
,p_button_plug_id=>wwv_flow_imp.id(104444646536494202)
,p_button_name=>'AGREGAR_FAV'
,p_button_action=>'DEFINED_BY_DA'
,p_button_template_options=>'#DEFAULT#'
,p_button_template_id=>wwv_flow_imp.id(40187078917263678)
,p_button_image_alt=>'Agregar Fav'
,p_button_position=>'EDIT'
,p_warn_on_unsaved_changes=>null
,p_button_condition=>wwv_flow_string.join(wwv_flow_t_varchar2(
'DECLARE',
'VEXISTE NUMBER;',
'BEGIN',
'    SELECT 1',
'      INTO VEXISTE',
'      FROM ASP$FAVO0100',
'     WHERE USRN = :APP_USER',
'       AND PAGE = :APP_PAGE_ID',
'       AND APLI0100$ID = :P_APLI0100_ID;',
'    RETURN FALSE;    ',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        RETURN TRUE;',
'END;'))
,p_button_condition2=>'PLSQL'
,p_button_condition_type=>'FUNCTION_BODY'
,p_icon_css_classes=>'fa-heart-o'
);
wwv_flow_imp_page.create_page_button(
 p_id=>wwv_flow_imp.id(103904073405744604)
,p_button_sequence=>20
,p_button_plug_id=>wwv_flow_imp.id(104444646536494202)
,p_button_name=>'QUITAR_FAV'
,p_button_action=>'DEFINED_BY_DA'
,p_button_template_options=>'#DEFAULT#'
,p_button_template_id=>wwv_flow_imp.id(40187078917263678)
,p_button_image_alt=>'Prueba'
,p_button_position=>'EDIT'
,p_warn_on_unsaved_changes=>null
,p_button_condition=>wwv_flow_string.join(wwv_flow_t_varchar2(
'DECLARE',
'VEXISTE NUMBER;',
'BEGIN',
'    SELECT 1',
'      INTO VEXISTE',
'      FROM ASP$FAVO0100',
'     WHERE USRN = :APP_USER',
'       AND PAGE = :APP_PAGE_ID',
'       AND APLI0100$ID = :P_APLI0100_ID;',
'    RETURN TRUE;    ',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        RETURN FALSE;',
'END;'))
,p_button_condition2=>'PLSQL'
,p_button_condition_type=>'FUNCTION_BODY'
,p_icon_css_classes=>'fa-heart'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(12523956006514401)
,p_name=>'P_COD_EMPLEADO'
,p_item_sequence=>110
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(12524143967514403)
,p_name=>'P_COD_CUSTODIO'
,p_item_sequence=>120
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(12524207331514404)
,p_name=>'P_COD_VENDEDOR'
,p_item_sequence=>130
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(12524337501514405)
,p_name=>'P_COD_COBRADOR'
,p_item_sequence=>140
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(12525731640514419)
,p_name=>'PO_SEARCH_NM'
,p_item_sequence=>10
,p_item_plug_id=>wwv_flow_imp.id(12525684456514418)
,p_display_as=>'PLUGIN_SI.ABAKUS.SEARCHNAVIGATIONMENU'
,p_attribute_01=>'S'
,p_attribute_02=>'fa-search'
,p_attribute_03=>wwv_flow_string.join(wwv_flow_t_varchar2(
'{"MenuOpen":false,',
' "MenuClickOpenClose":true,',
' "SaveSS":true,',
' "ShortcutSaveSS":false,',
' "ShrtCaseSensitive":true,',
' "OnSearchShowChildren":true,',
' "UseFocus":false,',
' "Shortcuts" : []',
'}'))
,p_attribute_04=>wwv_flow_string.join(wwv_flow_t_varchar2(
'/* ',
'** STYLE Settings for search navigation menu and menu icons',
'*/',
'/* FIX If you use FONT awesome enable this .srch_nav span */',
'/*',
'.srch_nav span { ',
'   top:2px;',
'}',
'*/',
'/* FIX If you use FONT awesome disable  this .t-TreeNav */',
'.t-TreeNav .a-TreeView-node--topLevel ul .a-TreeView-content .fa {',
'   vertical-align: top;',
'   width: 32px; /* This can be decrease to have smaller spacing */',
'   height: 32px;',
'   line-height: 32px;',
'   text-align: center;',
'   transition: width .2s ease;',
'}',
'/* Search resault setting */',
'.a-TreeView-label strong {',
'    font-weight:bold; ',
'    color:black;',
'    background-color:#ffef9a;',
'}',
'/* Input field style setting */',
'.srch_nav input {',
'    color:black;',
'    background-color:#f1f6fa;',
'    border-color:#ededed;',
'}',
'/* Input field on hover setting */',
'.srch_nav input:focus {',
'    border-color:#ff7052;',
'}'))
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(18332878544230335)
,p_name=>'P_ROLE0100_ID'
,p_item_sequence=>150
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40329872780321626)
,p_name=>'P_APLI0100_ID'
,p_item_sequence=>10
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_use_cache_before_default=>'NO'
,p_source=>'1'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40329940786321627)
,p_name=>'P_USUA0100_ID'
,p_item_sequence=>30
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40330122574321629)
,p_name=>'P_COD_EMPRESA'
,p_item_sequence=>60
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40330239458321630)
,p_name=>'P_NOM_EMPRESA'
,p_item_sequence=>70
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40330316107321631)
,p_name=>'P_COD_SUCURSAL'
,p_item_sequence=>80
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40330427311321632)
,p_name=>'P_NOM_SUCURSAL'
,p_item_sequence=>90
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(40330552959321633)
,p_name=>'P_COD_MODULO'
,p_item_sequence=>100
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(41117143023000701)
,p_name=>'P_COD_USUARIO'
,p_item_sequence=>40
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(44078860122498545)
,p_name=>'P_COD_EJERCICIO'
,p_item_sequence=>160
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(45558500908746519)
,p_name=>'P_VER_OTROS_VENDEDORES'
,p_item_sequence=>190
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(46968323012983618)
,p_name=>'P_DESCRIPCION_SUCURSAL'
,p_item_sequence=>170
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(52348265406603234)
,p_name=>'P0_VALIDACION_FECHA'
,p_item_sequence=>100
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(52866919981687033)
,p_name=>'P0_MENSAJE_VALIDACION'
,p_item_sequence=>220
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_use_cache_before_default=>'NO'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(54299381017918014)
,p_name=>'P0_MENSAJE'
,p_item_sequence=>200
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(54299452921918015)
,p_name=>'P0_ERROR'
,p_item_sequence=>210
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(71083569653541843)
,p_name=>'P0_VALIDACION_HORA'
,p_item_sequence=>90
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(72003724374704102)
,p_name=>'P0_KEY_CODE'
,p_item_sequence=>230
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(74640252015730501)
,p_name=>'P_DESCRIPCION_EMPRESA'
,p_item_sequence=>180
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(121291726422956206)
,p_name=>'P_GDRIVE_ID'
,p_item_sequence=>240
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(121291805261956207)
,p_name=>'P_GDRIVE_FOLDER'
,p_item_sequence=>250
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(188180925089669319)
,p_name=>'P0_ARTICULOS'
,p_item_sequence=>10
,p_item_plug_id=>wwv_flow_imp.id(188180867684669318)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250693771585243205)
,p_name=>'P0_ACCION_NOTIF'
,p_item_sequence=>10
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250693900602243207)
,p_name=>'P0_NUM_SELECT'
,p_item_sequence=>20
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250694063501243208)
,p_name=>'P0_DESTINATARIO'
,p_item_sequence=>30
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250694119074243209)
,p_name=>'P0_ID_GENERIC'
,p_item_sequence=>40
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250694265876243210)
,p_name=>'P0_URL'
,p_item_sequence=>50
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250694341831243211)
,p_name=>'P0_NOM_REMITENTE'
,p_item_sequence=>60
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250694487854243212)
,p_name=>'P0_ASUNTO'
,p_item_sequence=>70
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(250695055252243218)
,p_name=>'P0_SIGUE'
,p_item_sequence=>80
,p_item_plug_id=>wwv_flow_imp.id(250693843151243206)
,p_use_cache_before_default=>'NO'
,p_item_default=>'N'
,p_display_as=>'NATIVE_HIDDEN'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(503822734361299943)
,p_name=>'P_RND'
,p_item_sequence=>20
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_use_cache_before_default=>'NO'
,p_source=>'1'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(653214321176190113)
,p_name=>'P_ABREV_EMPRESA'
,p_item_sequence=>50
,p_item_plug_id=>wwv_flow_imp.id(40329574666321623)
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(322676400807845503)
,p_name=>'Expand'
,p_event_sequence=>5
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(322676520351845504)
,p_event_id=>wwv_flow_imp.id(322676400807845503)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'',
'$("#t_TreeNav").on("treeviewactivatenode", function(e, ui) { ',
'    var n$ = $(e.originalEvent.target).closest(".a-TreeView-content"); ',
'    if (ui.nodes.length > 0 && ui.nodes[0].link === "#") {//porque el link es hastag si usamos nativo de apex queda comilla vacia ',
'        if (n$.parent().hasClass("is-expandable")) { ',
'            $(this).treeView("expand", n$) ',
'        } else if (n$.parent().hasClass("is-collapsible")) { ',
'            $(this).treeView("collapse", n$) ',
'        } ',
'    } ',
'});'))
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(16977525891602917)
,p_name=>'CARGAR_PAGINA'
,p_event_sequence=>10
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
,p_display_when_type=>'EXISTS'
,p_display_when_cond=>wwv_flow_string.join(wwv_flow_t_varchar2(
'select PAGE_MODE',
' from APEX_220100.APEX_APPLICATION_PAGES',
' where workspace  = (SELECT S.workspace FROM APEX_220100.APEX_APPLICATIONS S WHERE S.application_id = :APP_ID) ',
' and page_id = :APP_PAGE_ID',
' and application_id = :APP_ID',
' --and :workspace_id = 2715162693355865',
' AND :APP_USER NOT IN (''HSEGOVIA'')',
' and page_mode = ''Normal'';'))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(250693500641243203)
,p_event_id=>wwv_flow_imp.id(16977525891602917)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'setInterval(function () {',
'        apex.item(''P0_ACCION_NOTIF'').setValue(''s'')',
'   }, 5000);'))
,p_server_condition_type=>'EXISTS'
,p_server_condition_expr1=>wwv_flow_string.join(wwv_flow_t_varchar2(
'SELECT *',
'FROM',
'APEX_WORKSPACE_SESSIONS',
'WHERE',
'APEX_SESSION_ID = v(''APP_SESSION'')'))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(16977648802602918)
,p_event_id=>wwv_flow_imp.id(16977525891602917)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_APEX.FLOATING.BUTTON.MENU'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'{',
'  "refresh":0,',
'  "btnColor": "#F44336",',
'  "btnIcon":"fa-plus",',
'  "btnIconColor": "white",',
'  "btnIconHover": "fa-send",',
'  "btnPositionBottom": "45px",',
'  "btnPositionRight": "45px",',
'  "btnRippleColor": "#e3cb12",',
'  "linkTargetBlank": true,',
'  "rippleEffect": true,',
'  "position": "static"',
'}',
''))
,p_attribute_02=>'floating-menu'
,p_attribute_04=>wwv_flow_string.join(wwv_flow_t_varchar2(
'SELECT',
'    /* icon of the float button when closed - only first row is used */',
'    ''fa-envelope-user'' AS BTN_ICON,',
'    /* color of the float button - only first row is used */',
'    /*''linear-gradient(60deg, hsl('' || ROUND(MOD((TRUNC(SYSDATE) - SYSDATE) * 1000000,350)) ||'', 79%, 45%), hsl('' || ROUND(MOD((TRUNC(SYSDATE) - SYSDATE) * 1000000,350))||'', 60%, 45%))''*/ ''#003a85'' AS BTN_COLOR,',
'    /* color of the float button ripple - only first row is used */',
'    /*''hsl('' || ROUND(MOD((TRUNC(SYSDATE) - SYSDATE) * 1000000,350)) ||'', 79%, 45%)''*/ ''#e8c70b'' AS BTN_RIPPLE_COLOR,',
'    /* color of the float button icon - only first row is used */',
'    ''#ffee00e4'' AS BTN_ICON_COLOR,',
'    /* icon of the float button when opened - only first row is used */',
'    /*''fa-close''*/''fa-send'' AS BTN_ICON_HOVER,',
'    /* position from bottom of body - only first row is used */',
'    ''30px'' AS BTN_POSITION_BOTTOM,',
'    /* position from right of body - only first row is used */',
'    ''30px'' AS BTN_POSITION_RIGHT,',
'    /* icon of the item in list */',
'    CASE ROWNUM',
'      WHEN 1 THEN ''#APP_FILES#aviso.png''',
'    END AS ITEM_ICON,',
'    /* text of the item in list */',
'    CASE ROWNUM',
'      WHEN 1 THEN ''Tienes mensaje(s) pendiente(s)''',
'      ',
'    END AS ITEM_TEXT,',
'    /* text color of the item in list */',
'    ''yellow'' AS ITEM_TEXT_COLOR,',
'    /* text background color of the item in list */',
'    ''#0076df'' AS ITEM_TEXT_BACKGROUND,',
'    /* link of the item in list */',
'    CASE ROWNUM',
'      WHEN 1 THEN ''f?p=122:96:'' ||v(''app_session'') ',
'    END AS ITEM_LINK,',
'    /* open link as in new tab */',
'    1 AS ITEM_LINK_BLANK,',
'    /* color of the item in list */',
'    CASE ROWNUM',
'      WHEN 1 THEN ''#0076df''',
'    END AS ITEM_COLOR,',
'    /* icon color of the item in list */',
'    CASE ROWNUM',
'      WHEN 1 THEN ''yellow''',
'',
'    END AS ITEM_ICON_COLOR',
'FROM',
'    DUAL ',
'WHERE 0 < (select count(*) CANTIDAD',
'             from BSV_MENSAJES_APEX',
'            where DESTINATARIO = :APP_USER',
'              AND TIPO = ''APEX'')',
''))
,p_attribute_05=>'N'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(250694641705243214)
,p_name=>'Cambiar_Accion_Notif'
,p_event_sequence=>30
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_ACCION_NOTIF'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(250694758499243215)
,p_event_id=>wwv_flow_imp.id(250694641705243214)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_EXECUTE_PLSQL_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'SELECT B.NUM_SELECT,',
'       B.DESTINATARIO,',
'       B.ID_GENERIC,',
'       B.URL,',
'       B.NOM_REMITENTE,',
'       B.ASUNTO,',
'       ''S''',
'  INTO :P0_NUM_SELECT,',
'       :P0_DESTINATARIO,',
'       :P0_ID_GENERIC,',
'       :P0_URL,',
'       :P0_NOM_REMITENTE,',
'       :P0_ASUNTO,',
'       :P0_SIGUE',
'  FROM BSV_MENSAJES_APEX B',
' WHERE B.DESTINATARIO = :APP_USER',
'   AND ROWNUM = 1 ',
'   AND B.ID_GENERIC NOT IN (SELECT N.ID_GENERICO FROM BS_NOTIF_DESKTOP N WHERE N.NRO_SELECT = B.NUM_SELECT AND N.USUARIO = B.DESTINATARIO)',
'',
' ORDER BY B.FECHA;',
'',
' EXCEPTION ',
' WHEN NO_DATA_FOUND THEN ',
'  :P0_SIGUE := ''N'';'))
,p_attribute_03=>'P0_NUM_SELECT,P0_DESTINATARIO,P0_URL,P0_NOM_REMITENTE,P0_ASUNTO,P0_ID_GENERIC,P0_SIGUE'
,p_attribute_04=>'N'
,p_attribute_05=>'PLSQL'
,p_wait_for_result=>'Y'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(250694824133243216)
,p_event_id=>wwv_flow_imp.id(250694641705243214)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'var vSigue = apex.item(''P0_SIGUE'').getValue();',
'if (vSigue == ''S''){',
'dispara_notificacion();',
'}',
'     ',
'    ',
'  ',
'function dispara_notificacion() {let permission = Notification.permission;',
' var vTitle = apex.item(''P0_NOM_REMITENTE'').getValue();',
'     var vBody = apex.item(''P0_ASUNTO'').getValue();',
'if(permission === "granted"){',
'   showNotification();',
'} else if(permission === "default"){',
'   requestAndShowPermission();',
'',
'}',
'',
'function requestAndShowPermission() {',
'    Notification.requestPermission(function (permission) {',
'        if (permission === "granted") {',
'            showNotification();',
'        }',
'    });',
'}',
'function showNotification() {',
'  //  if(document.visibilityState === "visible") {',
'  //      return;',
'  //  }',
'  ',
'   let title = vTitle;',
'   let icon = ''#APP_FILES#icons/app-icon-192.png''; //this is a large image may take more time to show notifiction, replace with small size icon',
'   let body = vBody;',
'',
'   let notification = new Notification(title, { body, icon });',
'',
'   notification.onclick = () => {',
'          notification.close();',
'          window.parent.focus();',
'          /*event.preventDefault(); // prevent the browser from focusing the Notification''s tab*/',
'           window.open(apex.item(''P0_URL'').getValue(), ''_blank'');',
'   }',
'   ',
'}',
'}'))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(250694944532243217)
,p_event_id=>wwv_flow_imp.id(250694641705243214)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_EXECUTE_PLSQL_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
' IF :P0_NUM_SELECT IS NOT NULL AND :P0_ID_GENERIC IS NOT NULL AND :P0_SIGUE = ''S'' THEN',
'INSERT INTO BS_NOTIF_DESKTOP S',
'             (S.NRO_SELECT,',
'              S.ID_GENERICO,',
'              S.FECHA_NOTIF,',
'              S.USUARIO )',
'              VALUES',
'              (:P0_NUM_SELECT,',
'               :P0_ID_GENERIC,',
'               to_date(TO_CHAR(SYSDATE,''DD/MM/YYYY HH24:MI:SS''),''DD/MM/YYYY HH24:MI:SS''),',
'               :APP_USER);',
'END IF;'))
,p_attribute_02=>'P0_NUM_SELECT,P0_ID_GENERIC,P0_SIGUE'
,p_attribute_05=>'PLSQL'
,p_wait_for_result=>'Y'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(52348387487603235)
,p_name=>'Validar dia'
,p_event_sequence=>40
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_FECHA'
,p_condition_element=>'P0_VALIDACION_FECHA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'1'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52348567582603237)
,p_event_id=>wwv_flow_imp.id(52348387487603235)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52348413733603236)
,p_event_id=>wwv_flow_imp.id(52348387487603235)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>unistr('D\00EDa no v\00E1lido')
,p_attribute_07=>'autodismiss:prevent-duplicates:remove-notifications:escape-html:newest-on-top:client-side-substitutions:dismiss-on-click:dismiss-on-button'
,p_attribute_08=>'top-right'
,p_attribute_09=>'Y'
,p_attribute_11=>'3'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52348650192603238)
,p_event_id=>wwv_flow_imp.id(52348387487603235)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_FECHA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(52348707228603239)
,p_name=>'Validar mes'
,p_event_sequence=>50
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_FECHA'
,p_condition_element=>'P0_VALIDACION_FECHA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'2'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
end;
/
begin
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52348892847603240)
,p_event_id=>wwv_flow_imp.id(52348707228603239)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52348937203603241)
,p_event_id=>wwv_flow_imp.id(52348707228603239)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>unistr('Mes no v\00E1lido')
,p_attribute_07=>'autodismiss:prevent-duplicates:remove-notifications:escape-html:newest-on-top:client-side-substitutions:dismiss-on-click:dismiss-on-button'
,p_attribute_08=>'top-right'
,p_attribute_09=>'Y'
,p_attribute_11=>'3'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349066163603242)
,p_event_id=>wwv_flow_imp.id(52348707228603239)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_FECHA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(52349193902603243)
,p_name=>unistr('Validar a\00F1o')
,p_event_sequence=>60
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_FECHA'
,p_condition_element=>'P0_VALIDACION_FECHA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'3'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349288250603244)
,p_event_id=>wwv_flow_imp.id(52349193902603243)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349318670603245)
,p_event_id=>wwv_flow_imp.id(52349193902603243)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>unistr('A\00F1o no v\00E1lido')
,p_attribute_07=>'autodismiss:escape-html:newest-on-top:client-side-substitutions:dismiss-on-click:dismiss-on-button'
,p_attribute_08=>'top-right'
,p_attribute_09=>'Y'
,p_attribute_11=>'3'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349445620603246)
,p_event_id=>wwv_flow_imp.id(52349193902603243)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_FECHA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(52349590395603247)
,p_name=>'Validar formato '
,p_event_sequence=>70
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_FECHA'
,p_condition_element=>'P0_VALIDACION_FECHA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'4'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349686383603248)
,p_event_id=>wwv_flow_imp.id(52349590395603247)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349735762603249)
,p_event_id=>wwv_flow_imp.id(52349590395603247)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>'Formato de fecha incorrecto'
,p_attribute_07=>'autodismiss:prevent-duplicates:remove-notifications:escape-html:newest-on-top:client-side-substitutions:dismiss-on-click:dismiss-on-button'
,p_attribute_08=>'top-right'
,p_attribute_09=>'Y'
,p_attribute_11=>'3'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52349861205603250)
,p_event_id=>wwv_flow_imp.id(52349590395603247)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_FECHA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(52867010685687034)
,p_name=>'Muestra mensajes de alertas'
,p_event_sequence=>80
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_MENSAJE_VALIDACION'
,p_condition_element=>'P0_MENSAJE_VALIDACION'
,p_triggering_condition_type=>'NOT_NULL'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52867218481687036)
,p_event_id=>wwv_flow_imp.id(52867010685687034)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52867119146687035)
,p_event_id=>wwv_flow_imp.id(52867010685687034)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>'&P0_MENSAJE_VALIDACION.'
,p_attribute_07=>'autodismiss:prevent-duplicates:escape-html:newest-on-top:client-side-substitutions:dismiss-on-click:dismiss-on-button'
,p_attribute_08=>'top-right'
,p_attribute_09=>'Y'
,p_attribute_11=>'5'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(52867328272687037)
,p_event_id=>wwv_flow_imp.id(52867010685687034)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_MENSAJE_VALIDACION'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(71083611349541844)
,p_name=>unistr('Validaci\00F3n formato')
,p_event_sequence=>90
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_HORA'
,p_condition_element=>'P0_VALIDACION_HORA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'1'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(71084246993541850)
,p_event_id=>wwv_flow_imp.id(71083611349541844)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(71083784318541845)
,p_event_id=>wwv_flow_imp.id(71083611349541844)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>'El valor que introdujo no corresponde al formato hora/minuto.'
,p_attribute_09=>'N'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(77957753189448601)
,p_event_id=>wwv_flow_imp.id(71083611349541844)
,p_event_result=>'TRUE'
,p_action_sequence=>40
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_HORA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(71083836641541846)
,p_name=>unistr('Validaci\00F3n formato hora')
,p_event_sequence=>100
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_HORA'
,p_condition_element=>'P0_VALIDACION_HORA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'2'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(77958006579448604)
,p_event_id=>wwv_flow_imp.id(71083836641541846)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(71083904125541847)
,p_event_id=>wwv_flow_imp.id(71083836641541846)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>'El valor que introdujo en la Hora no corresponde, introduzca un digito entre 00 y 23'
,p_attribute_09=>'N'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(77957823717448602)
,p_event_id=>wwv_flow_imp.id(71083836641541846)
,p_event_result=>'TRUE'
,p_action_sequence=>40
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_HORA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(71084029426541848)
,p_name=>unistr('Validaci\00F3n formato minutos')
,p_event_sequence=>110
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P0_VALIDACION_HORA'
,p_condition_element=>'P0_VALIDACION_HORA'
,p_triggering_condition_type=>'EQUALS'
,p_triggering_expression=>'3'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(77958165486448605)
,p_event_id=>wwv_flow_imp.id(71084029426541848)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'clear-all'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(71084188412541849)
,p_event_id=>wwv_flow_imp.id(71084029426541848)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'PLUGIN_COM.FOS.NOTIFICATIONS'
,p_attribute_01=>'warning'
,p_attribute_02=>'static'
,p_attribute_03=>unistr('Atenci\00F3n')
,p_attribute_04=>'El valor que introdujo en los minutos no corresponde, introduzca un digito entre 00 y 59'
,p_attribute_09=>'N'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(77957953061448603)
,p_event_id=>wwv_flow_imp.id(71084029426541848)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_CLEAR'
,p_affected_elements_type=>'ITEM'
,p_affected_elements=>'P0_VALIDACION_HORA'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(103904145000744605)
,p_name=>'DA_AGREGAR'
,p_event_sequence=>120
,p_triggering_element_type=>'BUTTON'
,p_triggering_button_id=>wwv_flow_imp.id(103903911751744603)
,p_bind_type=>'bind'
,p_bind_event_type=>'click'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(103904214054744606)
,p_event_id=>wwv_flow_imp.id(103904145000744605)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_EXECUTE_PLSQL_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'DECLARE',
'VID NUMBER;',
'BEGIN',
'    SELECT ID',
'      INTO VID',
'      FROM ASP$MODU0300',
'     WHERE APLI0100$ID = :P_APLI0100_ID',
'       AND PAGE_ID = :APP_PAGE_ID',
'       AND ROWNUM = 1;',
'',
'    INSERT INTO ASP$FAVO0100(USRN, PAGE, APLI0100$ID, MODU0300$ID)',
'         VALUES (:APP_USER, :APP_PAGE_ID, :P_APLI0100_ID, VID);',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        APEX_DEBUG.ERROR(SQLERRM);         ',
'END;',
'        '))
,p_attribute_05=>'PLSQL'
,p_wait_for_result=>'Y'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(103905636655744620)
,p_event_id=>wwv_flow_imp.id(103904145000744605)
,p_event_result=>'TRUE'
,p_action_sequence=>50
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>'location.reload();'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(103904549088744609)
,p_name=>'DA_QUITAR'
,p_event_sequence=>130
,p_triggering_element_type=>'BUTTON'
,p_triggering_button_id=>wwv_flow_imp.id(103904073405744604)
,p_bind_type=>'bind'
,p_bind_event_type=>'click'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(103904618929744610)
,p_event_id=>wwv_flow_imp.id(103904549088744609)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_EXECUTE_PLSQL_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'BEGIN',
'    DELETE FROM ASP$FAVO0100',
'          WHERE USRN = :APP_USER ',
'            AND PAGE = :APP_PAGE_ID ',
'            AND APLI0100$ID = :P_APLI0100_ID;',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        APEX_DEBUG.ERROR(SQLERRM);-- P0_ERROR...             ',
'END;',
'        '))
,p_attribute_05=>'PLSQL'
,p_wait_for_result=>'Y'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(103905780782744621)
,p_event_id=>wwv_flow_imp.id(103904549088744609)
,p_event_result=>'TRUE'
,p_action_sequence=>40
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>'location.reload();'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(188898995809344296)
,p_name=>'Verifica ticket para llamar_1'
,p_event_sequence=>140
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
,p_display_when_type=>'CURRENT_PAGE_EQUALS_CONDITION'
,p_display_when_cond=>'575'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(188899829686344293)
,p_event_id=>wwv_flow_imp.id(188898995809344296)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>'setInterval(''contador()'',17000);'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(188900364751344292)
,p_event_id=>wwv_flow_imp.id(188898995809344296)
,p_event_result=>'TRUE'
,p_action_sequence=>30
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>'setInterval(''refrescargrilla()'',15000);'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(503822401927299940)
,p_name=>'doble_sesion'
,p_event_sequence=>150
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
,p_display_when_type=>'NEVER'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(503822521741299941)
,p_event_id=>wwv_flow_imp.id(503822401927299940)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
unistr('// Obtener el ID de sesi\00F3n actual de APEX'),
'var apexSessionId = apex.env.APP_SESSION;',
'',
unistr('// Verificar si ya hay una sesi\00F3n almacenada'),
'if (sessionStorage.getItem(''apexActiveSession'') === apexSessionId) {',
unistr('    // Mostrar mensaje y bloquear navegaci\00F3n'),
unistr('    alert("Ya tienes esta sesi\00F3n abierta en otra pesta\00F1a. Por favor, usa solo una pesta\00F1a.");'),
'    window.location.href = "about:blank"; // Bloquear carga',
'} else {',
unistr('    // Guardar la sesi\00F3n actual'),
'    sessionStorage.setItem(''apexActiveSession'', apexSessionId);',
'}',
'',
unistr('// Limpiar al cerrar la pesta\00F1a/navegador'),
'window.addEventListener(''beforeunload'', function() {',
'    sessionStorage.removeItem(''apexActiveSession'');',
'});'))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(503822640891299942)
,p_event_id=>wwv_flow_imp.id(503822401927299940)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
unistr('// Obtener el ID de sesi\00F3n de APEX'),
'var apexSessionId = apex.env.APP_SESSION;',
'',
unistr('// Verificar si ya hay una sesi\00F3n almacenada'),
'if (localStorage.getItem(''apexActiveSession'') === apexSessionId) {',
unistr('    // Mostrar mensaje y cerrar la pesta\00F1a duplicada'),
unistr('    alert("Ya tienes esta sesi\00F3n abierta en otra pesta\00F1a. Por favor, usa solo una pesta\00F1a.");'),
unistr('    window.close(); // Cierra la pesta\00F1a actual (si es posible)'),
unistr('    window.location.href = "about:blank"; // Bloquea la navegaci\00F3n'),
'} else {',
unistr('    // Guardar la sesi\00F3n actual en localStorage (persiste entre pesta\00F1as)'),
'    localStorage.setItem(''apexActiveSession'', apexSessionId);',
'}',
'',
unistr('// Limpiar al cerrar la pesta\00F1a (pero no siempre se ejecuta)'),
'window.addEventListener(''beforeunload'', function() {',
'    if (!localStorage.getItem(''keepSession'')) {',
'        localStorage.removeItem(''apexActiveSession'');',
'    }',
'});'))
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(503822839366299944)
,p_name=>'doble_sesion_1'
,p_event_sequence=>160
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
,p_display_when_type=>'NEVER'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(503822965995299945)
,p_event_id=>wwv_flow_imp.id(503822839366299944)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'// En Function and Global Variable Declaration',
'function launchIsolatedSession() {',
'    const randomId = Math.floor(Math.random() * 1000000);',
'    const url = new URL(window.location.href);',
'    ',
unistr('    // Fuerza nueva sesi\00F3n y limpia cache'),
'    url.searchParams.set(''session'', ''0'');',
'    url.searchParams.set(''clear'', ''cache'');',
'    ',
'    // Usa iframe con sandbox para aislamiento',
'    const iframe = document.createElement(''iframe'');',
'    iframe.sandbox = ''allow-same-origin allow-scripts allow-popups allow-forms'';',
'    iframe.src = url.toString() + ''&isolated='' + randomId;',
'    iframe.style.display = ''none'';',
'    ',
'    document.body.appendChild(iframe);',
'    setTimeout(() => {',
'        window.open(url.toString(), ''_blank'');',
'        document.body.removeChild(iframe);',
'    }, 1000);',
'}'))
);
end;
/
prompt --application/end_environment
begin
wwv_flow_imp.import_end(p_auto_install_sup_obj => nvl(wwv_flow_application_install.get_auto_install_sup_obj, false));
commit;
end;
/
set verify on feedback on define on
prompt  ...done
