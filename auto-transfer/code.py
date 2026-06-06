"""
USB File Transfer Between Two Systems
=======================================
Simulates transferring files via a USB drive between System A and System B.

Rules:
  - USB can be plugged into ONLY ONE system at a time
  - System must be ON to plug in / use USB
  - When unplugged from one system → other system turns ON → USB plugged in
  - Routing table tells which file belongs to which system
  - USB acts as the intermediary "device" (like a real flash drive)

Flow:
  Source Folder
      │
      ▼
  [USB Drive] ── plugged into SystemA (ON)  →  copy file → unplug
                                                              │
                                              SystemA OFF ◄──┘
                                              SystemB ON
                                              USB plugged into SystemB
                                              copy file to SystemB inbox
                                              unplug USB
"""

import os
import shutil
import time
from pathlib import Path
from enum import Enum


# ──────────────────────────────────────────────
#  ROUTING TABLE  →  filename : destination
# ──────────────────────────────────────────────
ROUTING_TABLE = {
    "report.pdf":   "SystemA",
    "music.mp3":    "SystemB",
    "photo.jpg":    "SystemA",
    "notes.txt":    "SystemB",
    "data.csv":     "SystemA",
    "video.mp4":    "SystemB",
}


class SystemState(Enum):
    ON  = "ON "
    OFF = "OFF"


# ──────────────────────────────────────────────────
#  USB DRIVE
# ──────────────────────────────────────────────────
class USBDrive:
    """
    Represents a physical USB flash drive.
    Has its own storage folder. Tracks which system it's currently plugged into.
    """

    def __init__(self, usb_path: Path):
        self.path        = usb_path
        self.plugged_into = None          # None = unplugged
        self.path.mkdir(parents=True, exist_ok=True)

    @property
    def is_plugged_in(self):
        return self.plugged_into is not None

    def plug_into(self, system: "System"):
        """Plug USB into a specific system"""
        if self.is_plugged_in:
            raise RuntimeError(
                f"USB already plugged into {self.plugged_into.name}! Unplug first.")
        if system.state == SystemState.OFF:
            raise RuntimeError(
                f"Cannot plug USB into {system.name} — system is OFF!")
        self.plugged_into = system
        print(f"        🔌 USB plugged into [{system.name}]")
        time.sleep(0.3)

    def unplug(self):
        """Unplug USB safely"""
        if not self.is_plugged_in:
            return
        print(f"        ⏏  USB ejected from [{self.plugged_into.name}]")
        time.sleep(0.3)
        self.plugged_into = None

    def load_file(self, src: Path):
        """Copy a file FROM source INTO the USB drive."""
        if not self.is_plugged_in:
            raise RuntimeError("USB is not plugged in — cannot load file.")
        dest = self.path / src.name
        shutil.copy2(src, dest)
        print(f"        📥 File copied to USB: '{src.name}'")
        time.sleep(0.2)

    def deliver_file(self, filename: str, destination: "System"):
        """Copy a file FROM USB INTO the destination system's inbox."""
        if not self.is_plugged_in:
            raise RuntimeError("USB is not plugged in — cannot deliver file.")
        src  = self.path / filename
        dest = destination.inbox / filename
        shutil.copy2(src, dest)
        print(f"        📤 File copied to {destination.name} inbox: '{filename}'")
        time.sleep(0.2)

    def clear(self):
        """Wipe the USB drive after delivery."""
        for f in self.path.iterdir():
            f.unlink()
        print(f"        🗑  USB cleared (ready for next transfer)")
        time.sleep(0.2)


# ──────────────────────────────────────────────────
#  COMPUTER SYSTEM
# ──────────────────────────────────────────────────
class System:
    """A computer that can be turned ON or OFF."""

    def __init__(self, name: str, inbox: Path):
        self.name  = name
        self.inbox = inbox
        self.state = SystemState.OFF
        self.inbox.mkdir(parents=True, exist_ok=True)

    def power_on(self):
        """Turn system ON"""
        if self.state == SystemState.ON:
            print(f"        ✓ {self.name} already ON")
            return
        print(f"        ▶️  {self.name} powered ON")
        time.sleep(0.3)
        self.state = SystemState.ON

    def power_off(self):
        """Turn system OFF"""
        if self.state == SystemState.OFF:
            print(f"        ✓ {self.name} already OFF")
            return
        print(f"        ⏹️  {self.name} powered OFF")
        time.sleep(0.3)
        self.state = SystemState.OFF

    def __repr__(self):
        return f"System({self.name}, {self.state.value})"


# ──────────────────────────────────────────────────
#  TRANSFER MANAGER
# ──────────────────────────────────────────────────
class USBTransferManager:
    """
    Orchestrates the full USB transfer workflow:
      1. Read source file
      2. Identify destination from routing table
      3. Power ON the SOURCE system  → plug USB → load file → unplug
      4. Power OFF source system
      5. Power ON destination system → plug USB → deliver file → unplug
      6. Power OFF destination system
      7. Clear USB
      8. Repeat for next file
    """

    def __init__(self, source_folder: Path, usb_path: Path):
        self.source  = source_folder
        self.usb     = USBDrive(usb_path)
        self.systems = {
            "SystemA": System("SystemA", source_folder / "SystemA_inbox"),
            "SystemB": System("SystemB", source_folder / "SystemB_inbox"),
        }
        self.sender = System("Sender", source_folder)
        self.sender.state = SystemState.ON

    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_step(self, step_num, description):
        """Print a step indicator"""
        print(f"\n    ► STEP {step_num}: {description}")

    def print_separator(self):
        """Print a separator line"""
        print("\n" + "-" * 70)

    def transfer_file(self, file_path: Path, destination: "System"):
        """
        Transfer a single file via USB:
        1. Sender loads file onto USB
        2. Sender powers OFF
        3. Destination powers ON
        4. Destination receives file from USB
        5. Destination powers OFF
        6. USB cleared
        7. Sender powers ON for next transfer
        """
        fname = file_path.name
        dest_name = destination.name

        self.print_step(1, f"Sender loads '{fname}' onto USB")
        self.usb.plug_into(self.sender)
        self.usb.load_file(file_path)
        self.usb.unplug()

        self.print_step(2, f"Sender powers OFF")
        self.sender.power_off()

        self.print_step(3, f"{dest_name} powers ON")
        destination.power_on()

        self.print_step(4, f"USB plugged into {dest_name}, file delivery")
        self.usb.plug_into(destination)
        self.usb.deliver_file(fname, destination)
        self.usb.unplug()

        self.print_step(5, f"{dest_name} powers OFF")
        destination.power_off()

        self.print_step(6, f"USB cleared and ready")
        self.usb.clear()

        self.print_step(7, f"Sender powers back ON for next file")
        self.sender.power_on()

    def transfer_all(self):
        """Transfer all files from source to their destinations"""
        files = [f for f in self.source.glob("*.*")
                 if f.is_file() and not f.name.startswith(".")]

        if not files:
            print("No files found in source folder.")
            return

        self.print_header("USB FILE TRANSFER SIMULATION")
        print(f"\n  Source Folder : {self.source}")
        print(f"  USB Drive     : {self.usb.path}")
        print(f"  Files to transfer : {len(files)}")
        print(f"  Routing table : {ROUTING_TABLE}")

        file_count = 0
        success_count = 0

        for file_path in files:
            fname = file_path.name
            file_count += 1

            # Validate routing
            if fname not in ROUTING_TABLE:
                print(f"\n  ⚠️  SKIPPED: '{fname}' — no route found in ROUTING_TABLE")
                continue

            dest_name = ROUTING_TABLE[fname]
            if dest_name not in self.systems:
                print(f"\n  ⚠️  SKIPPED: '{fname}' — unknown destination '{dest_name}'")
                continue

            destination = self.systems[dest_name]

            # Print file transfer header
            self.print_separator()
            print(f"\n  FILE TRANSFER {file_count}")
            print(f"    Source    : {fname}")
            print(f"    Size      : {file_path.stat().st_size} bytes")
            print(f"    Destination : {dest_name}")
            print(f"    Path      : {destination.inbox}")

            try:
                self.transfer_file(file_path, destination)
                success_count += 1
                print(f"\n    ✅ TRANSFER COMPLETE for '{fname}'")
            except Exception as e:
                print(f"\n    ❌ TRANSFER FAILED for '{fname}': {e}")

        # Final summary
        self.print_separator()
        self.print_header("TRANSFER SESSION SUMMARY")

        print(f"\n  Total files processed : {file_count}")
        print(f"  Successful transfers  : {success_count}")
        print(f"  Failed transfers      : {file_count - success_count}")

        for name, sys in self.systems.items():
            received = list(sys.inbox.iterdir())
            print(f"\n  {name} Inbox ({len(received)} files):")
            for f in received:
                print(f"      ✓ {f.name} ({f.stat().st_size} bytes)")

        print("\n" + "=" * 70)
        print("  ✅ ALL TRANSFERS COMPLETE")
        print("=" * 70)


# ──────────────────────────────────────────────────
#  DEMO  — creates dummy files and runs the transfer
# ──────────────────────────────────────────────────
def create_demo_files(folder: Path):
    """Create sample files for demonstration"""
    folder.mkdir(parents=True, exist_ok=True)
    for fname in ROUTING_TABLE:
        path = folder / fname
        if not path.exists():
            path.write_text(f"Demo content of {fname}\n" * 5)
    
    # unrouted file to show skip behavior
    extra = folder / "orphan_file.log"
    if not extra.exists():
        extra.write_text("This file has no route in ROUTING_TABLE.")


if __name__ == "__main__":
    BASE   = Path("usb_transfer_demo")
    SOURCE = BASE / "source"
    USB    = BASE / "usb_drive"

    # Clean up old demo if exists
    if BASE.exists():
        shutil.rmtree(BASE)

    create_demo_files(SOURCE)
    manager = USBTransferManager(SOURCE, USB)
    manager.transfer_all()
