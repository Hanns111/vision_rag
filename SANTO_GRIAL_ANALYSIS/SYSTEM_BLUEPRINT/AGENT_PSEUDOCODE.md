# Pseudocódigo del agente (abstracto)

No es implementación; describe la forma del control de flujo observable en la arquitectura de referencia.

---

## Sesión interactiva (alto nivel)

```
función ejecutar_sesión_interactiva():
    inicializar_entorno_global()
    montar_ui_repl()

    mientras sesión_activa:
        evento = esperar_evento_ui()   # tecla, submit, comando, cancelación, etc.

        si evento es envío_de_prompt:
            await procesar_submit(evento)

        si evento es salida:
            romper

    finalizar_sesión_limpia()
```

---

## Un turno del agente (propuesto → modelo → herramientas)

```
función procesar_submit(payload):
    await hooks_previos_a_llamada()

    si payload es_comando_slash:
        ejecutar_comando_o_encolar()
        retornar

    mensajes = construir_mensajes(payload)
    contexto_herramientas = construir_tool_context(mensajes)
    prompt_sistema = construir_system_prompt_efectivo()

    para cada evento de ejecutar_turno(mensajes, prompt_sistema, contexto_herramientas):
        actualizar_ui(evento)        # tokens, tool_use, errores, etc.
```

---

## Núcleo del motor (queryLoop, conceptual)

```
generador ejecutar_turno(mensajes, system_prompt, tool_context):
    estado = estado_inicial(mensajes, tool_context)

    mientras turno_no_terminal(estado):
        # Llamada al modelo (remoto)
        respuesta = await servicio_modelo.proxima_iteración(
            estado.mensajes,
            system_prompt,
            herramientas_disponibles
        )

        emitir_eventos_stream(respuesta)

        si respuesta pide_uso_de_herramienta:
            si no permitido_por_política(herramienta):
                emitir_bloque_denegado()
                continuar

            resultado_tool = await ejecutar_herramienta(herramienta, argumentos)
            estado.mensajes = añadir_tool_result(estado.mensajes, resultado_tool)
            continuar

        si respuesta es_mensaje_asistente_final_o_stop:
            estado = marcar_fin_turno(estado)

        si necesita_compactar_contexto(estado):
            estado = compactar(estado)

    retornar terminal(estado)
```

---

## Relación con la UI

```
mientras haya eventos en ejecutar_turno(...):
    repl.mostrar_o_mutar_estado(evento)
```

---

## Observaciones

- **Varias** iteraciones modelo ↔ herramienta pueden ocurrir **dentro de un mismo** “enter” del usuario.
- **Compactación** y **reintentos** son ramas internas del motor, no de la REPL.
- En productos reales, **cancelación** (`AbortController` conceptual) debe cortar el generador del turno.
