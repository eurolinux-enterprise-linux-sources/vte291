%global apiver 2.91

Name:           vte291
Version:        0.52.2
Release:        2%{?dist}
Summary:        Terminal emulator library

License:        LGPLv2+
URL:            http://www.gnome.org/

Source0:        http://download.gnome.org/sources/vte/0.52/vte-%{version}.tar.xz
Source1:        %{name}-git.mk

# https://bugzilla.gnome.org/show_bug.cgi?id=711059
# https://bugzilla.redhat.com/show_bug.cgi?id=1103380
Patch100:       %{name}-command-notify-scroll-speed.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1443504
# https://bugzilla.redhat.com/show_bug.cgi?id=1590537
Patch101:       %{name}-restore-gnome-pty-helper.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1569801
Patch102:       %{name}-avoid-braced-initialization.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  gettext
BuildRequires:  pkgconfig(gnutls)
BuildRequires:  gobject-introspection-devel
BuildRequires:  gperf
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  intltool
BuildRequires:  vala

# initscripts creates the utmp group
Requires:       initscripts
Requires:       vte-profile

Conflicts:      gnome-terminal < 3.20.1-2

%description
VTE is a library implementing a terminal emulator widget for GTK+. VTE
is mainly used in gnome-terminal, but can also be used to embed a
console/terminal in games, editors, IDEs, etc.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

# vte-profile is deliberately not noarch to avoid having to obsolete a noarch
# subpackage in the future when we get rid of the vte3 / vte291 split. Yum is
# notoriously bad when handling noarch obsoletes and insists on installing both
# of the multilib packages (i686 + x86_64) as the replacement.
%package -n     vte-profile
Summary:        Profile script for VTE terminal emulator library
License:        GPLv3+
# vte.sh was previously part of the vte3 package
Conflicts:      vte3 < 0.36.1-3

%description -n vte-profile
The vte-profile package contains a profile.d script for the VTE terminal
emulator library.

%prep
%setup -q -n vte-%{version}
%patch100 -p1 -b .command-notify-scroll-speed
%patch101 -p1 -b .restore-gnome-pty-helper
%patch102 -p1 -b .avoid-braced-initialization

%build
install -m 0644 %{SOURCE1} ./git.mk
autoreconf --force --install

CFLAGS="%optflags -fPIE -DPIE -Wno-nonnull" \
CXXFLAGS="$CFLAGS" \
LDFLAGS="$LDFLAGS -Wl,-z,relro -Wl,-z,now -pie" \
%configure \
        --disable-static \
        --libexecdir=%{_libdir}/vte-%{apiver} \
        --disable-gtk-doc \
        --enable-gnome-pty-helper \
        --enable-introspection
make %{?_smp_mflags} V=1

%install
%make_install

rm -f $RPM_BUILD_ROOT%{_libdir}/*.la

%find_lang vte-%{apiver}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files -f vte-%{apiver}.lang
%license COPYING
%doc NEWS README
%{_libdir}/libvte-%{apiver}.so.0*
%dir %{_libdir}/vte-%{apiver}
%attr(2711,root,utmp) %{_libdir}/vte-%{apiver}/gnome-pty-helper
%{_libdir}/girepository-1.0/

%files devel
%{_bindir}/vte-%{apiver}
%{_includedir}/vte-%{apiver}/
%{_libdir}/libvte-%{apiver}.so
%{_libdir}/pkgconfig/vte-%{apiver}.pc
%{_datadir}/gir-1.0/
%doc %{_datadir}/gtk-doc/
%{_datadir}/vala/

%files -n vte-profile
%{_sysconfdir}/profile.d/vte.sh

%changelog
* Thu Jun 07 2018 Debarshi Ray <rishi@fedoraproject.org> - 0.52.2-2
- Fix race between gnome-pty-helper and VteTerminal
Resolves: #1569801, #1590537

* Thu Jun 07 2018 Debarshi Ray <rishi@fedoraproject.org> - 0.52.2-1
- Update to 0.52.2
Resolves: #1569801

* Tue May 23 2017 Debarshi Ray <rishi@fedoraproject.org> - 0.46.2-1
- Update to 0.46.2
- Backport upstream patch to remove an unused variable
Resolves: #1387056

* Mon May 22 2017 Debarshi Ray <rishi@fedoraproject.org> - 0.46.1-2
- Restore gnome-pty-helper
- Add git.mk and other dependencies to regenerate the build scripts
Resolves: #1443504

* Fri Feb 24 2017 Debarshi Ray <rishi@fedoraproject.org> - 0.46.1-1
- Update to 0.46.1
- Drop upstreamed patches
- Drop workaround for old GTK+ bug (#1238315)
- Rebase downstream patches
Resolves: #1387056

* Fri May 13 2016 Debarshi Ray <rishi@fedoraproject.org> - 0.38.4-2
- Add a property to configure the scroll speed
Resolves: #1103380

* Wed Mar 09 2016 Debarshi Ray <rishi@fedoraproject.org> - 0.38.4-1
- Update to 0.38.4
Resolves: #1303630

* Wed Feb 24 2016 Debarshi Ray <rishi@fedoraproject.org> - 0.38.3-3
- Backport support for CSI 3J (clear scrollback)
Resolves: #1186623

* Wed Jul 01 2015 Debarshi Ray <rishi@fedoraproject.org> - 0.38.3-2
- Don't hide the mouse pointer
Resolves: #1238315

* Fri Apr 17 2015 Debarshi Ray <rishi@fedoraproject.org> - 0.38.3-1
- Update to 0.38.3
Resolves: #1184192

* Tue Dec 02 2014 Debarshi Ray <rishi@fedoraproject.org> - 0.38.2-3
- Change default to TERM=xterm-256color (RH #1166428)

* Mon Dec 01 2014 Debarshi Ray <rishi@fedoraproject.org> - 0.38.2-2
- Backport upstream patch to fix zombie shells (GNOME #740929)

* Mon Nov 10 2014 Kalev Lember <kalevlember@gmail.com> - 0.38.2-1
- Update to 0.38.2

* Mon Oct 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.38.1-1
- Update to 0.38.1

* Sun Sep 14 2014 Kalev Lember <kalevlember@gmail.com> - 0.38.0-1
- Update to 0.38.0

* Mon Aug 18 2014 Kalev Lember <kalevlember@gmail.com> - 0.37.90-1
- Update to 0.37.90

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.37.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jul 22 2014 Kalev Lember <kalevlember@gmail.com> - 0.37.2-2
- Rebuilt for gobject-introspection 1.41.4

* Tue Jun 24 2014 Richard Hughes <rhughes@redhat.com> - 0.37.2-1
- Update to 0.37.2

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.37.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Kalev Lember <kalevlember@gmail.com> - 0.37.1-1
- Update to 0.37.1

* Wed May 07 2014 Kalev Lember <kalevlember@gmail.com> - 0.37.0-2
- Split out a vte-profile subpackage that can be used with both vte291 / vte3

* Tue May 06 2014 Kalev Lember <kalevlember@gmail.com> - 0.37.0-1
- Initial Fedora package, based on previous vte3 0.36 packaging
