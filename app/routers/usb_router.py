from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from ..controllers.serial_controller import SNESController, SNESButton

router = APIRouter()


class ButtonPress(BaseModel):
    buttons: List[str]
    duration: Optional[float] = 0.5


class SequenceItem(BaseModel):
    buttons: List[str]
    duration: float


class Sequence(BaseModel):
    name: str
    sequence: List[SequenceItem]


# Global controller instance (in production, use dependency injection)
controller = None


@router.on_event("startup")
async def startup_event():
    global controller
    try:
        controller = SNESController()
    except Exception as e:
        print(f"Failed to initialize controller: {e}")


@router.on_event("shutdown")
async def shutdown_event():
    global controller
    if controller:
        controller.close()


@router.post("/press")
async def press_buttons(button_press: ButtonPress):
    """Press a combination of buttons for a specified duration."""
    if not controller:
        raise HTTPException(status_code=500,
                            detail="Controller not initialized")

    try:
        buttons = []
        for btn_name in button_press.buttons:
            try:
                button = SNESButton[btn_name.upper()]
                buttons.append(button)
            except KeyError:
                raise HTTPException(status_code=400,
                                    detail=f"Unknown button: {btn_name}")

        controller.press_buttons(buttons)
        await asyncio.sleep(button_press.duration)
        controller.release_all()

        return {"status": "success", "pressed": [b.name for b in buttons]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record/start")
async def start_recording():
    """Start recording button presses (placeholder)."""
    # TODO: Implement recording logic
    return {"status": "recording started"}


@router.post("/record/stop")
async def stop_recording(filename: str):
    """Stop recording and save to file (placeholder)."""
    # TODO: Implement saving logic
    return {"status": "recording stopped", "saved_to": filename}


@router.post("/playback")
async def playback_sequence(sequence: Sequence):
    """Playback a sequence of button presses."""
    if not controller:
        raise HTTPException(status_code=500,
                            detail="Controller not initialized")

    try:
        for item in sequence.sequence:
            buttons = []
            for btn_name in item.buttons:
                try:
                    button = SNESButton[btn_name.upper()]
                    buttons.append(button)
                except KeyError:
                    raise HTTPException(status_code=400,
                                        detail=f"Unknown button: {btn_name}")

            controller.press_buttons(buttons)
            await asyncio.sleep(item.duration)
            controller.release_all()
            await asyncio.sleep(0.1)  # Small delay between actions

        return {"status": "success", "played": sequence.name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    """Get the current status of the USB client."""
    return {
        "controller_connected": controller is not None,
        "available_buttons": [b.name for b in SNESButton]
    }
