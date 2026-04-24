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
--   Date and Time:   16:16 Wednesday April 22, 2026
--   Exported By:     NZARATE
--   Flashback:       0
--   Export Type:     Page Export
--   Manifest
--     PAGE: 233
--   Manifest End
--   Version:         22.1.0
--   Instance ID:     203712190362964
--

begin
null;
end;
/
prompt --application/pages/delete_00233
begin
wwv_flow_imp_page.remove_page (p_flow_id=>wwv_flow.g_flow_id, p_page_id=>233);
end;
/
prompt --application/pages/page_00233
begin
wwv_flow_imp_page.create_page(
 p_id=>233
,p_user_interface_id=>wwv_flow_imp.id(40210426655263685)
,p_name=>'VTPEDIDOV'
,p_alias=>'VTPEDIDOV'
,p_step_title=>'VTPEDIDOV'
,p_autocomplete_on_off=>'OFF'
,p_page_template_options=>'#DEFAULT#'
,p_protection_level=>'C'
,p_page_component_map=>'18'
,p_last_updated_by=>'NZARATE'
,p_last_upd_yyyymmddhh24miss=>'20260325083056'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(56079088945779729)
,p_plug_name=>'VTPEDIDOV'
,p_region_template_options=>'#DEFAULT#'
,p_plug_template=>wwv_flow_imp.id(40123385688263660)
,p_plug_display_sequence=>20
,p_query_type=>'SQL'
,p_plug_source=>wwv_flow_string.join(wwv_flow_t_varchar2(
'WITH PedidosBase AS (',
'    -- Filtramos primero para reducir el volumen de datos de entrada',
'    SELECT * FROM VT_PEDIDOS_CABECERA',
'    WHERE COD_EMPRESA =  :p_cod_empresa',
'      AND FEC_COMPROBANTE BETWEEN TO_DATE(:P233_FECHA_INICIO,''dd/mm/yyyy'') AND TO_DATE(:P233_FECHA_FIN,''dd/mm/yyyy'')',
'      AND (COD_VENDEDOR = :P233_VENDEDOR OR :P233_VENDEDOR IS NULL)',
'),',
'DetalleMonto AS (',
'    -- Agrupamos el monto total de una vez',
'    SELECT cod_empresa, tip_comprobante, ser_comprobante, nro_comprobante,',
'           SUM(monto_total) as monto_total_det',
'    FROM vt_pedidos_detalle',
'    WHERE cod_empresa = :p_cod_empresa',
'    GROUP BY cod_empresa, tip_comprobante, ser_comprobante, nro_comprobante',
'),',
'Facturacion AS (',
'    -- Agrupamos las facturas asociadas',
'    SELECT f1.cod_empresa, f1.tip_comprobante_ref, f1.ser_comprobante_ref, f1.nro_comprobante_ref,',
'           LISTAGG(f1.tip_comprobante || ''-'' || f1.ser_comprobante || ''-'' || f1.nro_comprobante, ''; '')',
'           WITHIN GROUP (ORDER BY f1.nro_comprobante) as FACTURAS_LISTA',
'    FROM vt_comprobantes_cabecera f1',
'    WHERE f1.cod_empresa = :p_cod_empresa AND NVL(f1.estado, ''P'') <> ''A''',
'    GROUP BY f1.cod_empresa, f1.tip_comprobante_ref, f1.ser_comprobante_ref, f1.nro_comprobante_ref',
')',
'SELECT pb.imprimir,',
'       pb.cod_cliente,',
'       pb.nom_cliente,',
'       pb.tip_comprobante,',
'       pb.ser_comprobante,',
'       pb.nro_comprobante,',
'       pb.fec_comprobante,',
'       pb.cod_condicion_venta,',
'       dm.monto_total_det as MONTO_TOTAL,',
'       CASE WHEN pb.AUTORIZADO = ''S'' THEN ''AUTORIZADO''',
'            ELSE ''PENDIENTE''',
'       END autorizado,',
'       pb.estado_desc estado,',
'       pb.derivado,',
'       pb.entrega_remision,',
'       pb.ind_guarda,',
'       pb.ind_tipo_pedido,',
'       pb.observacion_interna,',
'       pb.observacion,',
'       pb.tipo_entrega,',
'       pb.cod_vendedor,',
'       pb.estado_distribucion_log,',
'       pb.cod_lista_precio,',
'       pb.desc_flete,',
'       pb.motivo_anulacion,',
'       --pb.*,',
'',
'       fa.FACTURAS_LISTA as FACTURA,',
'       CASE WHEN NVL(dm.monto_total_det, 0) > 0',
'           THEN ROUND((dm.monto_total_det - pb.costo_total_aprox) / dm.monto_total_det * 100, 2)',
'           ELSE 0 END as MARGEN',
'FROM (',
unistr('    -- Aqu\00ED incluimos el resto de tu l\00F3gica de columnas'),
'    SELECT CASE WHEN  a.tipo_entrega = ''CA'' THEN ''CAPITAL''',
'                WHEN a.TIPO_ENTREGA = ''IN'' THEN ''INTERIOR''',
'                WHEN a.TIPO_ENTREGA = ''CR'' THEN ''CLIENTE RETIRA''',
'           END  desc_tipo_entrega,',
'           a.*,',
unistr('           -- Simplificaci\00F3n de CASE de estados'),
'           DECODE(estado, ''P'', ''PENDIENTE'', ''F'', ''FACTURADO'', ''C'', ''CERRADO'', ''A'', ''ANULADO'') as ESTADO_DESC,',
unistr('           -- Evitar la subconsulta de fletes con un join si es posible, o dejarla si la tabla es peque\00F1a'),
'           (SELECT fl.descripcion FROM VT_FLETES FL WHERE FL.COD_EMPRESA = a.COD_EMPRESA AND FL.COD_FLETE = a.COD_FLETE) as DESC_FLETE,',
'           F_situacion_PEDIDO(a.ser_comprobante, a.nro_comprobante) as SITUACION,',
'           F_ESTADO_PEDIDO_logistica(A.ser_comprobante, A.nro_comprobante)estado_distribucion_log,',
'           NULL imprimir,',
'           (select descripcion from vt_motivo_anulacion z where z.cod_empresa=a.cod_empresa and z.cod_motivo_anu=a.cod_motivo_anu) motivo_anulacion,',
'           CASE WHEN Nvl(A.autorizado,''P'') =''S'' THEN ''AUTORIZADO''',
'                WHEN Nvl(A.autorizado,''P'') =''P'' THEN ''PENDIENTE''',
'                WHEN Nvl(deposito_fact,''X'') IS NOT NULL OR autorizado=''S'' THEN ''AUTORIZADO''',
'                WHEN nvl(A.autorizado,''N'')=''N'' THEN ''RECHAZADO''',
'                ELSE ''PENDIENTE''',
'           END AUTORIZACION,',
'           -- COSTO (Sigue siendo pesado, se recomienda una tabla de costos pre-calculada)',
'           -- Por ahora lo mantenemos igual pero fuera del bloque principal para claridad',
'           NVL((SELECT SUM(nvl(s.costo_prom_nue,0) / DECODE(a.cod_moneda,''2'',a.tip_cambio,1) * d.cantidad)',
'                FROM vt_pedidos_detalle d',
'                JOIN st_costos_art s ON s.cod_empresa = a.cod_empresa AND s.cod_articulo = d.cod_articulo',
'                WHERE d.cod_empresa = a.cod_empresa',
'                  AND d.tip_comprobante = a.tip_comprobante',
'                  AND d.ser_comprobante = a.ser_comprobante',
'                  AND d.nro_comprobante = a.nro_comprobante',
'                  AND s.tip_comprobante <> ''INI''',
'                  AND s.fec_proceso = (SELECT MAX(s2.fec_proceso)',
'                                       FROM st_costos_art s2',
'                                       WHERE s2.cod_empresa = a.cod_empresa',
'                                         AND s2.cod_articulo = d.cod_articulo',
'                                         AND s2.fec_proceso <= a.fec_comprobante)), 0) as costo_total_aprox,',
'           a.ROWID rowped',
'    FROM PedidosBase a',
') pb',
'LEFT JOIN DetalleMonto dm',
'  ON pb.cod_empresa = dm.cod_empresa',
' AND pb.tip_comprobante = dm.tip_comprobante',
' AND pb.ser_comprobante = dm.ser_comprobante',
' AND pb.nro_comprobante = dm.nro_comprobante',
'LEFT JOIN Facturacion fa',
'  ON pb.cod_empresa = fa.cod_empresa',
' AND pb.tip_comprobante = fa.tip_comprobante_ref',
' AND pb.ser_comprobante = fa.ser_comprobante_ref',
' AND pb.nro_comprobante = fa.nro_comprobante_ref',
'ORDER BY pb.fec_comprobante DESC',
''))
,p_plug_source_type=>'NATIVE_IR'
,p_ajax_items_to_submit=>'P233_VENDEDOR,P233_FECHA_INICIO,P233_FECHA_FIN'
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_prn_page_header=>'VTPEDIDOV'
);
wwv_flow_imp_page.create_worksheet(
 p_id=>wwv_flow_imp.id(56079126776779729)
,p_name=>'VTPEDIDOV'
,p_max_row_count_message=>unistr('El recuento m\00E1ximo de filas de este informe es #MAX_ROW_COUNT# filas. Aplique un filtro para reducir el n\00FAmero de registros de la consulta.')
,p_no_data_found_message=>unistr('No se ha encontrado ning\00FAn dato.')
,p_pagination_type=>'ROWS_X_TO_Y_OF_Z'
,p_pagination_display_pos=>'BOTTOM_RIGHT'
,p_report_list_mode=>'TABS'
,p_lazy_loading=>false
,p_show_detail_link=>'C'
,p_download_formats=>'CSV:HTML:XLSX:PDF'
,p_enable_mail_download=>'Y'
,p_detail_link=>'f?p=&APP_ID.:34:&SESSION.::&DEBUG.:RP,34:P34_PARAM_NRO_PED,P34_PARAM_SER_PED:\#NRO_COMPROBANTE#\,\#SER_COMPROBANTE#\'
,p_detail_link_text=>'<span aria-label="Editar"><span class="fa fa-edit" aria-hidden="true" title="Editar"></span></span>'
,p_owner=>'HSEGOVIA'
,p_internal_uid=>56079126776779729
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56080343983779735)
,p_db_column_name=>'TIP_COMPROBANTE'
,p_display_order=>3
,p_column_identifier=>'C'
,p_column_label=>'Tipo Comprobante'
,p_column_type=>'STRING'
,p_use_as_row_header=>'Y'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56080779075779736)
,p_db_column_name=>'SER_COMPROBANTE'
,p_display_order=>4
,p_column_identifier=>'D'
,p_column_label=>'Ser Comprobante'
,p_column_type=>'STRING'
,p_use_as_row_header=>'Y'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56081148575779736)
,p_db_column_name=>'NRO_COMPROBANTE'
,p_display_order=>5
,p_column_identifier=>'E'
,p_column_label=>'Nro. Comprobante'
,p_column_link=>'f?p=&APP_ID.:99:&SESSION.::&DEBUG.:CR,99:P99_NRO_COMPROBANTE_REF,P99_P_SER_COMPROBANTE_REF:#NRO_COMPROBANTE#,#SER_COMPROBANTE#'
,p_column_linktext=>'#NRO_COMPROBANTE#'
,p_column_type=>'NUMBER'
,p_use_as_row_header=>'Y'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56081966213779736)
,p_db_column_name=>'FEC_COMPROBANTE'
,p_display_order=>7
,p_column_identifier=>'G'
,p_column_label=>'Fecha Comprobante'
,p_column_type=>'DATE'
,p_column_alignment=>'CENTER'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56082371652779736)
,p_db_column_name=>'COD_CLIENTE'
,p_display_order=>8
,p_column_identifier=>'H'
,p_column_label=>'Cliente'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56082708427779736)
,p_db_column_name=>'COD_VENDEDOR'
,p_display_order=>9
,p_column_identifier=>'I'
,p_column_label=>'Vendedor'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56083190914779737)
,p_db_column_name=>'COD_CONDICION_VENTA'
,p_display_order=>10
,p_column_identifier=>'J'
,p_column_label=>unistr('Condici\00F3n Venta')
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56083504375779737)
,p_db_column_name=>'COD_LISTA_PRECIO'
,p_display_order=>11
,p_column_identifier=>'K'
,p_column_label=>'Lista Precio'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56086719783779739)
,p_db_column_name=>'ESTADO'
,p_display_order=>19
,p_column_identifier=>'S'
,p_column_label=>'Estado'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56092332768779742)
,p_db_column_name=>'NOM_CLIENTE'
,p_display_order=>33
,p_column_identifier=>'AG'
,p_column_label=>'Nom Cliente'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56099905582779746)
,p_db_column_name=>'AUTORIZADO'
,p_display_order=>52
,p_column_identifier=>'AZ'
,p_column_label=>'Autorizado'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56102769527779747)
,p_db_column_name=>'OBSERVACION'
,p_display_order=>59
,p_column_identifier=>'BG'
,p_column_label=>'Observacion'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56111928097779752)
,p_db_column_name=>'TIPO_ENTREGA'
,p_display_order=>82
,p_column_identifier=>'CD'
,p_column_label=>'Tipo Entrega'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56115195450779754)
,p_db_column_name=>'DERIVADO'
,p_display_order=>90
,p_column_identifier=>'CL'
,p_column_label=>'Derivado'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56123114641779757)
,p_db_column_name=>'IND_GUARDA'
,p_display_order=>110
,p_column_identifier=>'DF'
,p_column_label=>'Ind Guarda'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56125184830779758)
,p_db_column_name=>'ENTREGA_REMISION'
,p_display_order=>115
,p_column_identifier=>'DK'
,p_column_label=>'Entrega Remision'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56127971527779760)
,p_db_column_name=>'OBSERVACION_INTERNA'
,p_display_order=>122
,p_column_identifier=>'DR'
,p_column_label=>'Observacion Interna'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(56130717589779762)
,p_db_column_name=>'IND_TIPO_PEDIDO'
,p_display_order=>129
,p_column_identifier=>'DY'
,p_column_label=>'Ind Tipo Pedido'
,p_column_type=>'STRING'
,p_heading_alignment=>'LEFT'
,p_tz_dependent=>'N'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(156805743090017229)
,p_db_column_name=>'DESC_FLETE'
,p_display_order=>181
,p_column_identifier=>'EG'
,p_column_label=>'Flete'
,p_column_type=>'STRING'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(156806263308017234)
,p_db_column_name=>'ESTADO_DISTRIBUCION_LOG'
,p_display_order=>231
,p_column_identifier=>'EL'
,p_column_label=>'Estado Distribucion Log'
,p_column_type=>'STRING'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(172915302002833232)
,p_db_column_name=>'MONTO_TOTAL'
,p_display_order=>291
,p_column_identifier=>'ER'
,p_column_label=>'Monto Total'
,p_column_type=>'NUMBER'
,p_column_alignment=>'RIGHT'
,p_format_mask=>'999G999G999G999G999G999G999G999G999G990'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(172915403010833233)
,p_db_column_name=>'MARGEN'
,p_display_order=>301
,p_column_identifier=>'ES'
,p_column_label=>'Margen'
,p_column_type=>'NUMBER'
,p_column_alignment=>'RIGHT'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(76101538578162841)
,p_db_column_name=>'MOTIVO_ANULACION'
,p_display_order=>311
,p_column_identifier=>'ET'
,p_column_label=>'Motivo Anulacion'
,p_column_type=>'STRING'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(815771831827065948)
,p_db_column_name=>'IMPRIMIR'
,p_display_order=>331
,p_column_identifier=>'EV'
,p_column_label=>'Imprimir'
,p_column_link=>'javascript:$s(''P233_IMPRIMIR'',''#ROWPED#'');'
,p_column_linktext=>'<span class="fa fa-print" aria-hidden="true"></span>'
,p_column_type=>'STRING'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_column(
 p_id=>wwv_flow_imp.id(1619464432422491228)
,p_db_column_name=>'FACTURA'
,p_display_order=>341
,p_column_identifier=>'FB'
,p_column_label=>'Factura'
,p_column_type=>'STRING'
,p_use_as_row_header=>'N'
);
wwv_flow_imp_page.create_worksheet_rpt(
 p_id=>wwv_flow_imp.id(56134494748780191)
,p_application_user=>'APXWS_DEFAULT'
,p_report_seq=>10
,p_report_alias=>'561345'
,p_status=>'PUBLIC'
,p_is_default=>'Y'
,p_display_rows=>10
,p_report_columns=>'IMPRIMIR:COD_CLIENTE:NOM_CLIENTE:TIP_COMPROBANTE:SER_COMPROBANTE:NRO_COMPROBANTE:FEC_COMPROBANTE:COD_CONDICION_VENTA:MONTO_TOTAL:AUTORIZADO:ESTADO:DERIVADO:ENTREGA_REMISION:IND_GUARDA:IND_TIPO_PEDIDO:OBSERVACION_INTERNA:OBSERVACION:COD_VENDEDOR:ESTAD'
||'O_DISTRIBUCION_LOG:COD_LISTA_PRECIO:DESC_FLETE:MOTIVO_ANULACION:MARGEN'
,p_sort_column_1=>'FEC_COMPROBANTE'
,p_sort_direction_1=>'DESC NULLS LAST'
,p_sort_column_2=>'NRO_COMPROBANTE'
,p_sort_direction_2=>'DESC NULLS LAST'
,p_sort_column_3=>'0'
,p_sort_direction_3=>'ASC'
,p_sort_column_4=>'0'
,p_sort_direction_4=>'ASC'
,p_sort_column_5=>'0'
,p_sort_direction_5=>'ASC'
,p_sort_column_6=>'0'
,p_sort_direction_6=>'ASC'
);
wwv_flow_imp_page.create_worksheet_condition(
 p_id=>wwv_flow_imp.id(842665768920112808)
,p_report_id=>wwv_flow_imp.id(56134494748780191)
,p_condition_type=>'HIGHLIGHT'
,p_allow_delete=>'Y'
,p_column_name=>'AUTORIZADO'
,p_operator=>'='
,p_expr=>'AUTORIZADO'
,p_condition_sql=>' (case when ("AUTORIZADO" = #APXWS_EXPR#) then #APXWS_HL_ID# end) '
,p_condition_display=>'#APXWS_COL_NAME# = ''AUTORIZADO''  '
,p_enabled=>'Y'
,p_highlight_sequence=>10
,p_column_bg_color=>'#2bc618'
,p_column_font_color=>'#000000'
);
wwv_flow_imp_page.create_worksheet_condition(
 p_id=>wwv_flow_imp.id(842666168615112809)
,p_report_id=>wwv_flow_imp.id(56134494748780191)
,p_condition_type=>'HIGHLIGHT'
,p_allow_delete=>'Y'
,p_column_name=>'AUTORIZADO'
,p_operator=>'='
,p_expr=>'PENDIENTE'
,p_condition_sql=>' (case when ("AUTORIZADO" = #APXWS_EXPR#) then #APXWS_HL_ID# end) '
,p_condition_display=>'#APXWS_COL_NAME# = ''PENDIENTE''  '
,p_enabled=>'Y'
,p_highlight_sequence=>10
,p_column_bg_color=>'#f9ad16'
,p_column_font_color=>'#000000'
);
wwv_flow_imp_page.create_worksheet_condition(
 p_id=>wwv_flow_imp.id(842666576141112810)
,p_report_id=>wwv_flow_imp.id(56134494748780191)
,p_condition_type=>'HIGHLIGHT'
,p_allow_delete=>'Y'
,p_column_name=>'ESTADO'
,p_operator=>'='
,p_expr=>'FACTURADO'
,p_condition_sql=>' (case when ("ESTADO" = #APXWS_EXPR#) then #APXWS_HL_ID# end) '
,p_condition_display=>'#APXWS_COL_NAME# = ''FACTURADO''  '
,p_enabled=>'Y'
,p_highlight_sequence=>10
,p_column_bg_color=>'#2bc618'
,p_column_font_color=>'#000000'
);
wwv_flow_imp_page.create_worksheet_condition(
 p_id=>wwv_flow_imp.id(842666986627112811)
,p_report_id=>wwv_flow_imp.id(56134494748780191)
,p_condition_type=>'HIGHLIGHT'
,p_allow_delete=>'Y'
,p_column_name=>'ESTADO'
,p_operator=>'='
,p_expr=>'PENDIENTE'
,p_condition_sql=>' (case when ("ESTADO" = #APXWS_EXPR#) then #APXWS_HL_ID# end) '
,p_condition_display=>'#APXWS_COL_NAME# = ''PENDIENTE''  '
,p_enabled=>'Y'
,p_highlight_sequence=>10
,p_column_bg_color=>'#f9ad16'
,p_column_font_color=>'#000000'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(263386391525028467)
,p_plug_name=>'Filtro'
,p_region_template_options=>'#DEFAULT#:is-collapsed:t-Region--scrollBody'
,p_plug_template=>wwv_flow_imp.id(40108275410263656)
,p_plug_display_sequence=>10
,p_include_in_reg_disp_sel_yn=>'Y'
,p_plug_query_options=>'DERIVED_REPORT_COLUMNS'
,p_attribute_01=>'N'
,p_attribute_02=>'HTML'
);
wwv_flow_imp_page.create_page_plug(
 p_id=>wwv_flow_imp.id(209900000000000233)
,p_plug_name=>'Agente IA Comercial'
,p_region_template_options=>'#DEFAULT#:t-Region--scrollBody'
,p_plug_template=>wwv_flow_imp.id(40108275410263656)
,p_plug_display_sequence=>15
,p_include_in_reg_disp_sel_yn=>'Y'
,p_plug_source=>'<p style="color:#888;font-size:13px;margin:0;">Agente IA disponible en el bot&#243;n flotante (esquina inferior derecha).</p>'
);
wwv_flow_imp_page.create_page_button(
 p_id=>wwv_flow_imp.id(225196118135271925)
,p_button_sequence=>10
,p_button_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_button_name=>'Refrescar'
,p_button_action=>'DEFINED_BY_DA'
,p_button_template_options=>'#DEFAULT#:t-Button--iconRight'
,p_button_template_id=>wwv_flow_imp.id(40187845155263678)
,p_button_is_hot=>'Y'
,p_button_image_alt=>'Refrescar'
,p_button_position=>'NEXT'
,p_warn_on_unsaved_changes=>null
,p_icon_css_classes=>'fa-refresh'
);
wwv_flow_imp_page.create_page_button(
 p_id=>wwv_flow_imp.id(1630253285861468318)
,p_button_sequence=>10
,p_button_plug_id=>wwv_flow_imp.id(56079088945779729)
,p_button_name=>'AGENTE_IA'
,p_button_action=>'REDIRECT_URL'
,p_button_template_options=>'#DEFAULT#:t-Button--iconRight'
,p_button_template_id=>wwv_flow_imp.id(40187845155263678)
,p_button_is_hot=>'Y'
,p_button_image_alt=>'Agente IA'
,p_button_position=>'RIGHT_OF_IR_SEARCH_BAR'
,p_button_redirect_url=>'http://192.168.16.32:8080/ords/r/ngo/kairos/605?p605_user=&APP_USER.'
,p_button_condition=>'UPPER(:APP_USER)=''NZARATE'''
,p_button_condition2=>'PLSQL'
,p_button_condition_type=>'EXPRESSION'
,p_icon_css_classes=>'fa-plus'
);
wwv_flow_imp_page.create_page_button(
 p_id=>wwv_flow_imp.id(56132044374779763)
,p_button_sequence=>20
,p_button_plug_id=>wwv_flow_imp.id(56079088945779729)
,p_button_name=>'CREATE'
,p_button_action=>'REDIRECT_PAGE'
,p_button_template_options=>'#DEFAULT#:t-Button--iconRight'
,p_button_template_id=>wwv_flow_imp.id(40187845155263678)
,p_button_is_hot=>'Y'
,p_button_image_alt=>'Agregar'
,p_button_position=>'RIGHT_OF_IR_SEARCH_BAR'
,p_button_redirect_url=>'f?p=&APP_ID.:34:&SESSION.::&DEBUG.:CR,34:P34_PARAM_NRO_PED,P34_PARAM_SER_PED:,'
,p_icon_css_classes=>'fa-plus'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(225196597505271922)
,p_name=>'P233_VENDEDOR'
,p_item_sequence=>50
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_prompt=>'Vendedor'
,p_display_as=>'NATIVE_POPUP_LOV'
,p_lov=>wwv_flow_string.join(wwv_flow_t_varchar2(
'SELECT  P.NOMBRE ||''(''||F.COD_VENDEDOR||'')'' NOMBRE,F.COD_VENDEDOR FROM FV_VENDEDORES F, PERSONAS P',
'WHERE F.COD_EMPRESA=:p_cod_empresa',
'AND F.COD_PERSONA=P.COD_PERSONA',
'AND NVL(F.ESTADO,''I'')NOT IN ''I''',
'and (F.COD_VENDEDOR = :P_COD_VENDEDOR )',
'UNION ALL',
'SELECT  P.NOMBRE ||''(''||F.COD_VENDEDOR||'')'' NOMBRE,F.COD_VENDEDOR FROM FV_VENDEDORES F, PERSONAS P',
'WHERE F.COD_EMPRESA=:p_cod_empresa',
'AND F.COD_PERSONA=P.COD_PERSONA',
'AND NVL(F.ESTADO,''I'')NOT IN ''I''',
'',
' /*AND :P0_VER_OTROS_VENDEDORES = ''S''*/',
'ORDER BY 1'))
,p_lov_display_null=>'YES'
,p_lov_null_text=>'TODOS'
,p_cSize=>30
,p_field_template=>wwv_flow_imp.id(40186634462263678)
,p_item_icon_css_classes=>'fa-user-check'
,p_item_template_options=>'#DEFAULT#'
,p_lov_display_extra=>'YES'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'POPUP'
,p_attribute_02=>'FIRST_ROWSET'
,p_attribute_03=>'N'
,p_attribute_04=>'N'
,p_attribute_05=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(225197772280271919)
,p_name=>'P233_FECHA_INICIO'
,p_item_sequence=>80
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_prompt=>'Inicio'
,p_display_as=>'NATIVE_DATE_PICKER_JET'
,p_cSize=>30
,p_field_template=>wwv_flow_imp.id(40186634462263678)
,p_item_template_options=>'#DEFAULT#'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
,p_attribute_02=>'POPUP'
,p_attribute_03=>'NONE'
,p_attribute_06=>'NONE'
,p_attribute_09=>'N'
,p_attribute_11=>'Y'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(225198128103271919)
,p_name=>'P233_FECHA_FIN'
,p_is_required=>true
,p_item_sequence=>90
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_item_default=>'SYSDATE'
,p_item_default_type=>'EXPRESSION'
,p_item_default_language=>'PLSQL'
,p_prompt=>'Fecha Fin'
,p_display_as=>'NATIVE_DATE_PICKER'
,p_cSize=>30
,p_begin_on_new_line=>'N'
,p_field_template=>wwv_flow_imp.id(40186634462263678)
,p_item_template_options=>'#DEFAULT#'
,p_encrypt_session_state_yn=>'N'
,p_attribute_04=>'button'
,p_attribute_05=>'N'
,p_attribute_07=>'NONE'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(225198510350271918)
,p_name=>'P233_USUARIO'
,p_item_sequence=>100
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_source=>'&APP_USER.'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'Y'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(815771915839065949)
,p_name=>'P233_IMPRIMIR'
,p_item_sequence=>110
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_source=>'&APP_USER.'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'Y'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(842565215963550003)
,p_name=>'P233_SER_PEDIDO'
,p_item_sequence=>120
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_source=>'&APP_USER.'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'N'
);
wwv_flow_imp_page.create_page_item(
 p_id=>wwv_flow_imp.id(842565306026550004)
,p_name=>'P233_NRO_PEDIDO'
,p_item_sequence=>130
,p_item_plug_id=>wwv_flow_imp.id(263386391525028467)
,p_source=>'&APP_USER.'
,p_source_type=>'STATIC'
,p_display_as=>'NATIVE_HIDDEN'
,p_encrypt_session_state_yn=>'N'
,p_attribute_01=>'Y'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(56132337097779763)
,p_name=>unistr('Editar Informe: Cuadro de Di\00E1logo Cerrado')
,p_event_sequence=>10
,p_triggering_element_type=>'REGION'
,p_triggering_region_id=>wwv_flow_imp.id(56079088945779729)
,p_bind_type=>'bind'
,p_bind_event_type=>'apexafterclosedialog'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(56132875766779764)
,p_event_id=>wwv_flow_imp.id(56132337097779763)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_REFRESH'
,p_affected_elements_type=>'REGION'
,p_affected_region_id=>wwv_flow_imp.id(56079088945779729)
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(172916667435833245)
,p_name=>'REFRESCAR'
,p_event_sequence=>20
,p_triggering_element_type=>'BUTTON'
,p_triggering_button_id=>wwv_flow_imp.id(225196118135271925)
,p_bind_type=>'bind'
,p_bind_event_type=>'click'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(172916722432833246)
,p_event_id=>wwv_flow_imp.id(172916667435833245)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_REFRESH'
,p_affected_elements_type=>'REGION'
,p_affected_region_id=>wwv_flow_imp.id(56079088945779729)
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(815772037975065950)
,p_name=>'DA_IMPRIMIR'
,p_event_sequence=>30
,p_triggering_element_type=>'ITEM'
,p_triggering_element=>'P233_IMPRIMIR'
,p_bind_type=>'bind'
,p_bind_event_type=>'change'
);
wwv_flow_imp_page.create_page_da_event(
 p_id=>wwv_flow_imp.id(209900000000002233)
,p_name=>'INIT_AI_CHAT'
,p_event_sequence=>40
,p_bind_type=>'bind'
,p_bind_event_type=>'ready'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(209900000000003233)
 ,p_event_id=>wwv_flow_imp.id(209900000000002233)
,p_event_result=>'TRUE'
,p_action_sequence=>5
,p_execute_on_page_init=>'Y'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'(function(){var W=document.createElement(''div'');',
'W.innerHTML=''<div id=aiBtn_233 style="position:fixed;bottom:24px;right:24px;z-index:9999;width:54px;height:54px;border-radius:50%;background:#0572c6;color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 16px rgba(0,0,0,.35);font-size:26px;" title="Agente IA">&#128172;</div>''',
' +''<div id=aiPan_233 style="display:none;position:fixed;bottom:88px;right:24px;z-index:9998;width:520px;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.3);overflow:hidden;background:#fff;">''',
' +''<div style="background:#0572c6;color:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;"><b>Agente Comercial IA</b>''',
' +''<div style="display:flex;gap:8px;align-items:center;"><span id=aiClear_233 style="cursor:pointer;font-size:11px;padding:2px 8px;border-radius:4px;border:1px solid rgba(255,255,255,.5);">Vaciar</span>''',
' +''<span id=aiX_233 style="cursor:pointer;font-size:20px;">&times;</span></div></div>''',
' +''<div id=aiQA_233 style="background:#e8f0fe;padding:5px 10px;display:flex;gap:5px;flex-wrap:wrap;border-bottom:1px solid #d0d8f0;">''',
' +''<button id=qaV style="font-size:11px;padding:2px 7px;border-radius:3px;border:0;background:#fff;cursor:pointer;">&#128202; Ventas</button>''',
' +''<button id=qaK style="font-size:11px;padding:2px 7px;border-radius:3px;border:0;background:#fff;cursor:pointer;">&#128230; Stock</button>''',
' +''<button id=qaP style="font-size:11px;padding:2px 7px;border-radius:3px;border:0;background:#fff;cursor:pointer;">&#127919; Promos</button>''',
' +''<button id=qaC style="font-size:11px;padding:2px 7px;border-radius:3px;border:0;background:#fff;cursor:pointer;">&#128100; Clientes</button></div>''',
' +''<div id=aiH_233 style="height:390px;overflow-y:auto;padding:12px;background:#f4f6f8;"></div>''',
' +''<div id=aiCSV_233 style="display:none;padding:3px 10px;background:#fff;text-align:right;border-top:1px solid #eee;"><a id=aiCSVLnk href=# style="font-size:11px;color:#0572c6;">&darr; Exportar CSV</a></div>''',
' +''<div style="display:flex;gap:6px;padding:10px;background:#fff;border-top:1px solid #ddd;">''',
' +''<input id=aiI_233 type=text placeholder="Escribe tu pregunta..." style="flex:1;padding:8px 11px;border:1px solid #ccc;border-radius:6px;font-size:13px;text-transform:uppercase;">''',
' +''<button id=aiS_233 type=button style="padding:8px 14px;background:#0572c6;color:#fff;border:0;border-radius:6px;cursor:pointer;font-size:13px;">Enviar</button>''',
' +''</div></div>'';',
'document.body.appendChild(W);})();'
))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(209900000000004233)
 ,p_event_id=>wwv_flow_imp.id(209900000000002233)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'Y'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'(function(){',
'var d=document,SK=''AI_CTX_233'',API=''http://10.100.13.110:8010/chat'',lastDatos=null,B,P,inp,btn,CSV,lnk;',
'function esc(s){return(s||'''').replace(/&/g,''&amp;'').replace(/</g,''&lt;'').replace(/>/g,''&gt;'');}',
'function getC(){try{return JSON.parse(sessionStorage.getItem(SK)||''[]'');}catch(e){return[];}}',
'function setC(c){try{sessionStorage.setItem(SK,JSON.stringify(c));}catch(e){}}',
'function render(){var el=d.getElementById(''aiH_233'');if(!el)return;var c=getC(),h=[];',
'for(var i=0;i<c.length;i++){var m=c[i],u=m.role===''user'';',
'h.push(''<div style="margin:5px 0;padding:9px 12px;border-radius:10px;max-width:90%;background:''+(u?''#0572c6'':''#fff'')+'';color:''+(u?''#fff'':''#333'')+'';white-space:pre-line;''+(u?''margin-left:auto;text-align:right;'':'''')+''">''+(u?esc(m.content):m.content)+''</div>'');',
'}el.innerHTML=h.join('''');el.scrollTop=el.scrollHeight;}',
'function clearChat(){if(confirm(''Vaciar la conversacion?'')){setC([]);lastDatos=null;CSV.style.display=''none'';render();}}',
'function app(r,c){var x=getC();x.push({role:r,content:c});setC(x);render();}',
'function doCSV(){if(!lastDatos||!lastDatos.filas||!lastDatos.filas.length)return;',
'var cols=lastDatos.columnas||Object.keys(lastDatos.filas[0]);',
'var rows=[cols.join('','')];',
'var q=''"'';lastDatos.filas.forEach(function(r){',
'rows.push(cols.map(function(c){var v=String(r[c]||'''');return q+v.replace(/"/g,q+q)+q;}).join('',''));});',
'if(lnk){lnk.href=''data:text/csv;charset=utf-8,''+encodeURIComponent(rows.join(''\n''));lnk.download=''datos.csv'';}}',
'function send(m){',
'if(!m){if(!inp)return;m=(inp.value||'''').trim();if(!m)return;inp.value='''';}',
'm=m.toUpperCase();var hist=getC().slice(-6);app(''user'',m);',
'if(btn){btn.disabled=true;btn.textContent=''...'';}',
'var cod=null;try{cod=apex.item(''P_COD_EMPRESA'').getValue();}catch(e){}',
'var ven=null;try{ven=apex.item(''P_COD_VENDEDOR'').getValue();}catch(e){}',
'var otros=null;try{otros=apex.item(''P_VER_OTROS_VENDEDORES'').getValue();}catch(e){}',
'fetch(API,{method:''POST'',headers:{''Content-Type'':''application/json''},',
'body:JSON.stringify({mensaje:m,usuario:''&APP_USER.'',contexto:{cod_empresa:cod,cod_vendedor:ven,ver_otros_vendedores:otros,periodo:''mes''},historial:hist})})',
'.then(function(r){if(!r.ok)throw r.status;return r.json();})',
'.then(function(j){app(''assistant'',j&&j.respuesta?j.respuesta:''Sin respuesta.'');',
'if(j&&j.datos&&j.datos.filas&&j.datos.filas.length){lastDatos=j.datos;doCSV();CSV.style.display=''block'';}',
'else{lastDatos=null;CSV.style.display=''none'';}}).catch(function(){app(''assistant'',''Error al conectar con el agente IA.'');})',
'.finally(function(){if(btn){btn.disabled=false;btn.textContent=''Enviar'';}});}',
'B=d.getElementById(''aiBtn_233'');P=d.getElementById(''aiPan_233'');',
'inp=d.getElementById(''aiI_233'');btn=d.getElementById(''aiS_233'');',
'CSV=d.getElementById(''aiCSV_233'');lnk=d.getElementById(''aiCSVLnk'');',
'if(B)B.onclick=function(){P.style.display=P.style.display===''none''?''block'':''none'';',
'if(P.style.display===''block''){render();setTimeout(function(){inp.focus();},100);}};',
'd.getElementById(''aiX_233'').onclick=function(){P.style.display=''none'';};',
'd.getElementById(''aiClear_233'').onclick=clearChat;',
'btn.onclick=function(){send(null);};',
'inp.onkeydown=function(e){if(e.key===''Enter''){e.preventDefault();send(null);}};',
'var QA={qaV:''Top 10 productos mas vendidos del mes actual'',',
'qaK:''Articulos con stock critico o en cero'',',
'qaP:''Promociones vigentes activas hoy'',qaC:''Clientes sin compra en los ultimos 60 dias''};',
'Object.keys(QA).forEach(function(id){var el=d.getElementById(id);if(el)el.onclick=function(){send(QA[id]);};});',
'})();'
))
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(842565059099550001)
,p_event_id=>wwv_flow_imp.id(815772037975065950)
,p_event_result=>'TRUE'
,p_action_sequence=>10
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_EXECUTE_PLSQL_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'BEGIN',
'    SELECT SER_COMPROBANTE, NRO_COMPROBANTE',
'    INTO :P233_SER_PEDIDO, :P233_NRO_PEDIDO',
'',
'    FROM VT_PEDIDOS_CABECERA',
'    WHERE COD_EMPRESA = :P_COD_EMPRESA',
'    AND ROWID = :P233_IMPRIMIR;',
'    ',
'EXCEPTION',
'    WHEN OTHERS THEN',
'        APEX_DEBUG.ERROR(SQLERRM);',
'END;'))
,p_attribute_02=>'P233_IMPRIMIR,P_COD_EMPRESA'
,p_attribute_03=>'P233_SER_PEDIDO,P233_NRO_PEDIDO'
,p_attribute_04=>'N'
,p_attribute_05=>'PLSQL'
,p_wait_for_result=>'Y'
);
wwv_flow_imp_page.create_page_da_action(
 p_id=>wwv_flow_imp.id(842565424112550005)
,p_event_id=>wwv_flow_imp.id(815772037975065950)
,p_event_result=>'TRUE'
,p_action_sequence=>20
,p_execute_on_page_init=>'N'
,p_action=>'NATIVE_JAVASCRIPT_CODE'
,p_attribute_01=>wwv_flow_string.join(wwv_flow_t_varchar2(
'var comprobante = document.getElementById("P233_NRO_PEDIDO").value; ',
'var params = []',
'var empresa = apex.item("P_COD_EMPRESA").getValue();',
'var tip_comprobante =''PED'';',
'var ser_comprobante = apex.item("P233_SER_PEDIDO").getValue();',
'var nro_comprobante = apex.item("P233_NRO_PEDIDO").getValue();',
'',
'var usuario = ''&APP_USER.'';',
'var vfacnom = "VTPEDIDO";',
'params.push({ name: ''p_cod_empresa'', value: empresa})',
'params.push({ name: ''p_tip_comprobante'', value: tip_comprobante})',
'params.push({ name: ''p_ser_comprobante'', value: ser_comprobante}) ',
'params.push({ name: ''p_nro_comprobante'', value: nro_comprobante}) ',
'',
'createReportUrl(vfacnom, params)',
'',
'',
''))
);
wwv_flow_imp_page.create_page_process(
 p_id=>wwv_flow_imp.id(1152814384058848426)
,p_process_sequence=>10
,p_process_point=>'BEFORE_HEADER'
,p_process_type=>'NATIVE_PLSQL'
,p_process_name=>'New'
,p_process_sql_clob=>wwv_flow_string.join(wwv_flow_t_varchar2(
'BEGIN',
'  IF :P233_FECHA_INICIO IS NULL THEN',
'    :P233_FECHA_INICIO := TO_CHAR(SYSDATE-5, ''DD/MM/YYYY'');',
'  END IF;',
'  IF :P233_FECHA_FIN IS NULL THEN',
'    :P233_FECHA_FIN := TO_CHAR(SYSDATE, ''DD/MM/YYYY'');',
'  END IF;',
'END;'))
,p_process_clob_language=>'PLSQL'
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
