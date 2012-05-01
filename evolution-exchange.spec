%define intltool_version 0.35.5
%define libsoup_version 2.3.0

%define evo_major 2.28
%define eds_major 1.2

# Make sure the evolution package is upgraded first, or else this variable
# will come up empty and lead to the following libtool error.
#
# 	libtool: link: only absolute run-paths are allowed
#
# The error is caused by the -R ${plibdir} substitution below; -R requires
# an argument and libtool does not complain until late in the game.  Seems
# like it could be smarter about this.
%define plibdir %(pkg-config evolution-shell --variable=privlibdir 2>/dev/null)

### Abstract ###

Name: evolution-exchange
Version: 2.28.3
Release: 2%{?dist}
Group: Applications/Productivity
Summary: Evolution plugin to interact with MS Exchange Server
License: GPLv2+
URL: http://projects.gnome.org/evolution/
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
Source: http://download.gnome.org/sources/%{name}/2.28/%{name}-%{version}.tar.bz2
ExcludeArch: s390 s390x

Provides: evolution-connector = %{version}-%{release}
Obsoletes: evolution-connector < %{version}-%{release}

### Patches ###

Patch11: evolution-exchange-2.10.1-fix-64bit-acinclude.patch

### Dependencies ###

Requires: gnutls
Requires: openldap

### Build Dependencies ###

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: db4-devel
BuildRequires: evolution-data-server-devel >= %{version}
BuildRequires: evolution-devel >= %{version}
BuildRequires: gettext
BuildRequires: gnome-common
BuildRequires: gnutls-devel
BuildRequires: gtk-doc
BuildRequires: intltool >= %{intltool_version}
BuildRequires: libsoup-devel >= %{libsoup_version}
BuildRequires: libtool >= 1.5
BuildRequires: openldap-evolution-devel
BuildRequires: openssl-devel

%description
This package enables added functionality to Evolution when used with a 
Microsoft Exchange Server.

%prep
%setup -q -n evolution-exchange-%{version}

%patch11 -p1 -b .fix-64bit-acinclude

%build
export CFLAGS="$RPM_OPT_FLAGS -DLDAP_DEPRECATED"
# Set LIBS so that configure will be able to link with static LDAP libraries,
# which depend on Cyrus SASL and OpenSSL.
if pkg-config openssl ; then
	LIBS="-lsasl2 `pkg-config --libs openssl`"
else
	LIBS="-lsasl2 -lssl -lcrypto"
fi
export LIBS

# Regenerate configure to pick up acinclude.m4 changes.
autoreconf --force --install

%configure \
  --enable-gtk-doc \
  --with-openldap=%{_libdir}/evolution-openldap \
  --with-static-ldap

make %{?_smp_mflags} LDFLAGS="-R %{plibdir}"

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
rm -f $RPM_BUILD_ROOT/%{_libdir}/evolution-data-server-%{eds_major}/camel-providers/*.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/evolution-data-server-%{eds_major}/camel-providers/*.la
%find_lang evolution-exchange-%{evo_major}

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/apps_exchange_addressbook-%{evo_major}.schemas > /dev/null

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%files -f evolution-exchange-%{evo_major}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING INSTALL NEWS docs/active-directory
%doc docs/autoconfig docs/debug docs/forms
%doc docs/http
%{_bindir}/exchange-connector-setup-%{evo_major}
%{_libdir}/bonobo/servers/GNOME_Evolution_Exchange_Storage_%{evo_major}.server
%{_libdir}/evolution-data-server-%{eds_major}/camel-providers/libcamelexchange.so
%{_libdir}/evolution-data-server-%{eds_major}/camel-providers/libcamelexchange.urls
%{_libexecdir}/evolution/%{evo_major}/evolution-exchange-storage 
%{_datadir}/gtk-doc/html/evolution-exchange
%dir %{_datadir}/evolution-exchange
%dir %{_datadir}/evolution-exchange/%{evo_major}
%dir %{_datadir}/evolution-exchange/%{evo_major}/glade
%dir %{_datadir}/evolution-exchange/%{evo_major}/images
%dir %{_datadir}/evolution-exchange/%{evo_major}/ui
%{_datadir}/evolution-exchange/%{evo_major}/glade/*
%{_datadir}/evolution-exchange/%{evo_major}/images/*
%{_datadir}/evolution-exchange/%{evo_major}/ui/*
%{_sysconfdir}/gconf/schemas/apps_exchange_addressbook-%{evo_major}.schemas

%changelog
* Wed Mar 31 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-2.el6
- Don't install libtool archives (RH bug #564489).

* Tue Mar 02 2010 Matthew Barnes <mbarnes@redhat.com> - 2.28.3-1.el6
- Update to 2.28.3

* Wed Jan 13 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-3.el6
- Remove .m4 extension from a patch

* Wed Jan 13 2010 Milan Crha <mcrha@redhat.com> - 2.28.2-2.el6
- Correct Source URL
- Disable build on s390/s390x, because evolution is too

* Mon Dec 14 2009 Milan Crha <mcrha@redhat.com> - 2.28.2-1.fc12
- Update to 2.28.2

* Mon Oct 19 2009 Milan Crha <mcrha@redhat.com> - 2.28.1-1.fc12
- Update to 2.28.1

* Mon Sep 21 2009 Milan Crha <mcrha@redhat.com> - 2.28.0-1.fc12
- Update to 2.28.0

* Mon Sep 07 2009 Milan Crha <mcrha@redhat.com> - 2.27.92-1.fc12
- Update to 2.27.92

* Sun Aug 30 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.91-3.fc12
- Rebuild again.

* Thu Aug 27 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.91-2.fc12
- Rebuild with old OpenSSL, er something...

* Mon Aug 24 2009 Milan Crha <mcrha@redhat.com> - 2.27.91-1.fc12
- Update to 2.27.91

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.27.90-2
- rebuilt with new openssl

* Mon Aug 10 2009 Milan Crha <mcrha@redhat.com> - 2.27.90-1.fc12
- Update to 2.27.90

* Mon Jul 27 2009 Milan Crha <mcrha@redhat.com> - 2.27.5-1.fc12
- Update to 2.27.5

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.4-1.fc12
- Update to 2.27.4

* Wed Jul 01 2009 Milan Crha <mcrha@redhat.com> - 2.27.3-2.fc12
- Rebuild against newer gcc

* Mon Jun 15 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.3-1.fc12
- Update to 2.27.3

* Fri May 29 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.2-2.fc12
- Remove patch for GNOME bug #443022 (obsolete).

* Fri May 29 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.2-1.fc12
- Update to 2.27.2
- Remove strict_build_settings since the settings are used upstream now.

* Mon May 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.27.1-1.fc12
- Update to 2.27.1
- Bump evo_major to 2.28.

* Mon Apr 13 2009 Matthew Barnes <mbarnes@redhat.com> - 2.26.1-1.fc11
- Update to 2.26.1

* Mon Mar 16 2009 Matthew Barnes <mbarnes@redhat.com> - 2.26.0-1.fc11
- Update to 2.26.0

* Mon Mar 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.92-1.fc11
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.91-1.fc11
- Update to 2.25.91

* Fri Feb 06 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-2.fc11
- Update BuildRoot, License, Source and URL tags.
- Require gnome-common so we don't have to patch it out.

* Mon Feb 02 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.90-1.fc11
- Update to 2.25.90

* Mon Jan 19 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.5-1.fc11
- Update to 2.25.5
- Ditch eds_version and evo_version and use our own version.  This will
  keep evolution, evolution-exchange and evolution-data-server versions
  in lockstep from now on.

* Fri Jan 16 2009 Tomas Mraz <tmraz@redhat.com> - 2.25.4-2.fc11
- rebuild with new openssl

* Tue Jan 06 2009 Matthew Barnes <mbarnes@redhat.com> - 2.25.4-1.fc11
- Update to 2.25.4

* Mon Dec 15 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.3-1.fc11
- Update to 2.25.3

* Mon Dec 01 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.2-1.fc11
- Update to 2.25.2

* Mon Nov 03 2008 Matthew Barnes <mbarnes@redhat.com> - 2.25.1-1.fc11
- Update to 2.25.1
- Bump evo_major to 2.26.
- Bump evo_version and eds_version to 2.25.1.

* Tue Oct 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.1-2.fc10
- Bump eds_version to 2.24.1 (unfortunately).

* Tue Oct 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.1-1.fc10
- Update to 2.24.1

* Mon Sep 22 2008 Matthew Barnes <mbarnes@redhat.com> - 2.24.0-1.fc10
- Update to 2.24.0

* Thu Sep 18 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.92-2.fc10
- Fix unowned directories (RH bug #462346).

* Mon Sep 08 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.92-1.fc10
- Update to 2.23.92

* Mon Sep 01 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.91-1.fc10
- Update to 2.23.91
- Add -Werror to CFLAGS.

* Wed Aug 20 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.90-1.fc10
- Update to 2.23.90
- Bump eds_version to 2.23.90.1.

* Mon Aug 04 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.6-1.fc10
- Update to 2.23.6

* Mon Jul 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.5-1.fc10
- Update to 2.23.5
- Bump eds_version to 2.23.5.

* Fri Jul 18 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.23.4-2
- fix license tag
- fix source url

* Mon Jun 16 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.4-1.fc10
- Update to 2.23.4

* Mon Jun 02 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.3-1.fc10
- Update to 2.23.3

* Mon May 12 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.2-1.fc10
- Update to 2.23.2

* Mon Apr 21 2008 Matthew Barnes <mbarnes@redhat.com> - 2.23.1-1.fc10
- Update to 2.23.1
- Bump evo_major to 2.24.
- Bump evo_version to 2.23.1.
- Bump eds_version to 2.23.1.

* Mon Apr 07 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.1-1.fc9
- Update to 2.22.1

* Mon Mar 10 2008 Matthew Barnes <mbarnes@redhat.com> - 2.22.0-1.fc9
- Update to 2.22.0

* Mon Feb 25 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.92-1.fc9
- Update to 2.21.92
- Disable -Werror since libical now insists on emitting #warnings.

* Wed Feb 13 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.91-2.fc9
- Rebuild against libsoup 2.3.2.

* Mon Feb 11 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.91-1.fc9
- Update to 2.21.91
- Disable strict-aliasing due to GNOME bug #316221 and GCC 4.3.

* Mon Jan 28 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.90-1.fc9
- Update to 2.21.90
- Update build requirements.

* Mon Jan 14 2008 Matthew Barnes <mbarnes@redhat.com> - 2.21.5-1.fc9
- Update to 2.21.5

* Mon Dec 17 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.4-1.fc9
- Update to 2.21.4
- Bump eds_version to 2.21.4 for new Camel functions.

* Wed Dec 05 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.3-2.fc9
- Bump eds_version to 2.21.3.

* Mon Dec 03 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.3-1.fc9
- Update to 2.21.3

* Mon Nov 12 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.2-1.fc9
- Update to 2.21.2

* Sun Nov 04 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.1-2.fc9
- Remove obsolete patches.

* Mon Oct 29 2007 Matthew Barnes <mbarnes@redhat.com> - 2.21.1-1.fc9
- Update to 2.21.1
- Remove redundant requirements.
- Bump evo_version and eds_version to 2.21.1.

* Mon Oct 15 2007 Milan Crha <mcrha@redhat.com> - 2.12.1-1.fc8
- Update to 2.12.1
- Removed evolution-exchange-2.11.92-compilation-breakage.patch (fixed upstream).
- Removed evolution-exchange-2.12.0-warnings.patch (fixed upstream).

* Mon Sep 17 2007 Matthew Barnes <mbarnes@redhat.com> - 2.12.0-1.fc8
- Update to 2.12.0

* Mon Sep 03 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.92-1.fc8
- Update to 2.11.92

* Tue Aug 28 2007 Milan Crha <mcrha@redhat.com> - 2.11.91-1.fc8
- Update to 2.11.91
- Removed patch for GNOME bug #466987 (fixed upstream).

* Wed Aug 15 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.90-1.fc8
- Update to 2.11.90
- Add patch for GNOME bug #466987 (glibc redefines "open").
- Remove -DGNOME_DISABLE_DEPRECATED since GnomeDruid is now deprecated.

* Wed Aug 01 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.6.1-1.fc8
- Update to 2.11.6.1
- Remove patch for GNOME bug #380534 (fixed upstream).

* Fri Jul 27 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.5-2.fc8
- Add patch for GNOME bug #380534 (clarify version requirements).

* Mon Jul 09 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.5-1.fc8
- Update to 2.11.5

* Mon Jun 18 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.4-1.fc8
- Update to 2.11.4
- Remove patch for GNOME bug #444101 (fixed upstream).

* Wed Jun 06 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.3.1-2.fc8
- Rename package to evolution-exchange, obsoletes evolution-connector.

* Mon Jun 04 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.3.1-1.fc8
- Update to 2.11.3.1
- Add patch for GNOME bug #444101 (new compiler warnings).
- Remove patch for GNOME bug #439579 (fixed upstream).

* Fri Jun 01 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.2-2.fc8
- List static ldap libraries in the proper order.
- Compile with -Werror.

* Fri May 18 2007 Matthew Barnes <mbarnes@redhat.com> - 2.11.2-1.fc8
- Update to 2.11.2
- Bump evo_version to 2.11.0, eds_version to 1.11.0, and evo_major to 2.12.
- Remove evolution-exchange-2.5.3-fix-marshaller.patch (obsolete).
- Remove patch for GNOME bug #405916 (fixed upstream).

* Thu Apr 26 2007 Matthew Barnes <mbarnes@redhat.com> - 2.10.1-3.fc7
- Regenerate configure to pick up 64-bit changes to acinclude.m4.
- Require autoconf and automake to build.

* Thu Apr 26 2007 Matthew Barnes <mbarnes@redhat.com> - 2.10.1-2.fc7
- Fix a misnamed macro (RH bug #237807).

* Mon Apr 09 2007 Matthew Barnes <mbarnes@redhat.com> - 2.10.1-1.fc7
- Update to 2.10.1
- Add -Wdeclaration-after-statement to strict build settings.

* Mon Mar 12 2007 Matthew Barnes <mbarnes@redhat.com> - 2.10.0-1.fc7
- Update to 2.10.0

* Tue Feb 27 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.92-2.fc7
- Add missing libgnomeprint22 requirements.
- Add flag to disable deprecated GNOME symbols.

* Mon Feb 26 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.92-1.fc7
- Update to 2.9.92
- Reverting -Werror due to bonobo-i18n.h madness.
- Add minimum version to intltool requirement (currently >= 0.35.5).

* Mon Feb 12 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.91-2.fc7
- Fix some 64-bit compiler warnings.

* Mon Feb 12 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.91-1.fc7
- Update to 2.9.91
- Compile with -Werror.
- Add BuildRequires db4-devel.
- Add flags to disable deprecated Pango and GTK+ symbols.
- Add patch for GNOME bug #405916 (fix all compiler warnings).
- Remove patch for GNOME bug #360240 (superseded).

* Sun Jan 21 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.5-2.fc7
- Revise evolution-exchange-2.7.2-no_gnome_common.patch so that we no longer
  have to run autoconf before building.

* Mon Jan 08 2007 Matthew Barnes <mbarnes@redhat.com> - 2.9.5-1.fc7
- Update to 2.9.5
- Remove patch for GNOME bug #357660 (fixed upstream).

* Tue Dec 19 2006 Matthew Barnes <mbarnes@redhat.com> - 2.9.4-1.fc7
- Update to 2.9.4
- Require evolution-data-server-1.9.4.

* Mon Dec 04 2006 Matthew Barnes <mbarnes@redhat.com> - 2.9.3-1.fc7
- Update to 2.9.3
- Require evolution-data-server-1.9.3.
- Add %post section to install new schemas file.
- Remove evolution-exchange-2.8.1-bump-requirements.patch (fixed upstream).

* Tue Oct 24 2006 Matthew Barnes <mbarnes@redhat.com> - 2.8.1-2.fc7
- Add patch and rebuild for next Evolution development cycle.

* Mon Oct 16 2006 Matthew Barnes <mbarnes@redhat.com> - 2.8.1-1.fc7
- Update to 2.8.1
- Use stricter build settings.
- Add patch for Gnome.org bug #360340 ("unused variable" warnings).

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 2.8.0-3.fc6
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Mon Sep 25 2006 Matthew Barnes <mbarnes@redhat.com> - 2.8.0-2.fc6
- Add patch for Gnome.org bug #357660.

* Mon Sep  4 2006 Matthew Barnes <mbarnes@redhat.com> - 2.8.0-1.fc6
- Update to 2.8.0
- Remove patch for Gnome.org bug #349949 (fixed upstream).

* Mon Aug 21 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.92-1
- Update to 2.7.92

* Mon Aug  7 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.91-2
- Rebuild against correct evolution-data-server.

* Mon Aug  7 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.91-1
- Update to 2.7.91

* Sat Aug  5 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.90-3
- Fix eds_major (bumped it when I shouldn't have).

* Sat Aug  5 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.90-1
- Update to 2.7.90

* Wed Jul 12 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.4-1
- Update to 2.7.4

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.7.3-2.1
- rebuild

* Wed Jun 14 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.3-2
- Rebuild 

* Wed Jun 14 2006 Matthias Clasen <mclasen@redhat.com> - 2.7.3-1
- Update to 2.7.3

* Wed May 24 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.2-2
- Add BuildRequires for gtk-doc (closes #192251).
- Require specific versions of GNU Autotools packages for building.
- Various spec file cleanups.

* Wed May 17 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.2-1
- Update to 2.7.2
- Update spec file to run the autotools itself after patching.
- Remove evolution-exchange-2.7.1-fix_version.patch; fixed upstream.
- Remove unused or obsolete patches:
  evolution-connector-2.0.2-domain-fix.patch
  evolution-connector-2.7.2-generated-autotool.patch
  ximian-connector-2.1.4-fix-convenience-libraries.patch
  ximian-connector-2.2.2-install-debug-utilities.patch
  ximian-connector-2.2.2-noinst-ltlibraries.patch
- Add evolution-exchange-2.7.2-no_gnome_common.patch; removes
  GNOME_COMPILE_WARNINGS from configure.in.

* Sun May 14 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.1-2
- Forgot to add evolution-exchange-2.7.1-fix_version.patch to CVS.

* Fri May 12 2006 Matthew Barnes <mbarnes@redhat.com> - 2.7.1-1
- Update to 2.7.1
- Add some comments about the `plibdir' variable.
- Add --enable-gtk-doc to the `configure' invocation.
- Add temporary patch evolution-exchange-2.7.1-fix_version.patch.

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.6.1-2
- Update to 2.6.1

* Mon Mar 13 2006 Ray Strode <rstrode@redhat.com> - 2.6.0-1
- 2.6.0

* Tue Feb 28 2006 Ray Strode <rstrode@redhat.com> - 2.5.92-1
- 2.5.92

* Wed Feb 15 2006 David Malcolm <dmalcolm@redhat.com> - 2.5.91-1
- 2.5.91
- fix missing declarations (patch 301)

* Mon Feb 13 2006 Jesse Keating <jkeating@redhat.com> - 2.5.9.0-2.2.1
- rebump for build order issues during double-long bump

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.5.9.0-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.5.9.0-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Ray Strode <rstrode@redhat.com> - 2.5.9.0-2
- add builddeps (bug 137879)

* Mon Jan 30 2006 David Malcolm <dmalcolm@redhat.com> - 2.5.9.0-1
- 2.5.9.0
- regenerate patch 200
- enable parallel make

* Wed Jan 25 2006 David Malcolm <dmalcolm@redhat.com> - 2.5.5.1-1
- 2.5.5.1
- regenerate patch 200

* Wed Jan  4 2006 David Malcolm <dmalcolm@redhat.com> - 2.5.4-1
- 2.5.4

* Mon Dec 19 2005 David Malcolm <dmalcolm@redhat.com> - 2.5.3-1
- 2.5.3
- regenerate patch 200
- add patch to use correct marshalling code (patch 300)
- dropped glob of etspec files

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Dec  7 2005 David Malcolm <dmalcolm@redhat.com> - 2.5.2-1
- 2.5.2
- bump evo_major from 2.4 to 2.6
- bump evolution requirement from 2.4.1 to 2.5.2 to ensure we get an appropriate
  underlying version of evolution
- regenerate patch 200

* Fri Dec  2 2005 David Malcolm <dmalcolm@redhat.com> - 2.4.2-1
- 2.4.2
- regenerate patch 200; forcing regeneration of intltool scripts to 
  keep them in sync with our aclocal/intltool.m4
 
* Tue Nov 29 2005 David Malcolm <dmalcolm@redhat.com> - 2.4.1-3
- add -DLDAP_DEPRECATED to CFLAGS (#172999)

* Wed Nov  9 2005 Tomas Mraz <tmraz@redhat.com> - 2.4.1-2
- rebuilt with new openssl

* Tue Oct 18 2005 David Malcolm <dmalcolm@redhat.com> - 2.4.1-1
- 2.4.1
- bump evolution requirement to 2.4.1 and libsoup requirement to 2.2.6.1
- fix URL to point to 2.4, not 2.3

* Thu Sep 15 2005 Jeremy Katz <katzj@redhat.com> - 2.4.0-2
- rebuild for new e-d-s

* Wed Sep  7 2005 David Malcolm <dmalcolm@redhat.com> - 2.4.0-1
- 2.4.0
- Regenerated patch 200

* Wed Aug 24 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.8-1
- 2.3.8
- Regenerated patch 200
- Add -Werror-implicit-function-declaration to CFLAGS; make it use RPM_OPT_FLAGS

* Mon Aug 15 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.7-2
- rebuild

* Tue Aug  9 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.7-1
- 2.3.7
- Bump evolution requirement from 2.3.5.1 to 2.3.7
- Bump libsoup requirement from 2.2.2 to 2.2.5
- Remove ximian-connector-2.0.4-fix-sync-callback.patch; a slightly modified 
  version of this is now in the upstream tarball (#139393)

* Mon Aug  8 2005 Tomas Mraz <tmraz@redhat.com> - 2.3.6-3
- rebuild with new gnutls

* Mon Aug  1 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.6-2
- bump evo_major from 2.2 to 2.4
- Removed the various test programs (they no longer exist in the upstream 
  tarball)
- Renamed more instances of "ximian-connector" to "evolution-exchange" as
  appropriate.

* Thu Jul 28 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.6-1
- 2.3.6

* Tue Jul 26 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.5-2
- increase evolution requirement to 2.3.5.1

* Mon Jul 25 2005 David Malcolm <dmalcolm@redhat.com> - 2.3.5-1
- 2.3.5
- Changed various references to source tarball name from ximian-connector to
  evolution-exchange and updated the URL
- Remove Patch101 and Patch102 from autotool source patches and regenerate 
  resulting post-autotool patch

* Wed May 18 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.2-5
- add Aaron Gaudio's patch to fix PDA syncronization (#139393)

* Tue May 17 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.2-4
- Install the debug utilities from the "lib" subdirectory; renumber patches 
  accordingly; regenerate the generated patch

* Wed May  4 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.2-3
- updated noinst patch: libexchange is now a convenience library again; use -R
syntax to express path to Evolution's private libraries rather than -Wl since
libtool cannot properly intrepret the latter; regenerated resulting patch.

* Mon May  2 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.2-2
- disabling noinst patch as not yet applied

* Mon Apr 11 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.2-1
- 2.2.2

* Thu Mar 17 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.1-1
- 2.2.1
- Regenerated autotool patch

* Wed Mar  9 2005 David Malcolm <dmalcolm@redhat.com> - 2.2.0-1
- 2.2.0
- Updated evolution dependency to 2.2.0

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.6-3
- reapply the 64bit multilib LDAP patch, and regenerate the autotool patch accordingly

* Tue Mar  1 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.6-2
- actually remove the convenience library patches this time

* Wed Feb  9 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.6-1
- Update from unstable upstream 2.1.5 to 2.1.6
- Require evolution 2.1.6
- Removed patches for convenience libraries as these are now upstream

* Wed Feb  9 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.5-1
- Update from unstable upstream 2.1.4 to 2.1.5
- Require evolution 2.1.5

* Mon Feb  7 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.4-3
- Patch to fix non-portable usage of convenience libraries; reorganised the hand-edited vs generated patches (generated patch is 990K in size)
- Add "-Wl" to make arguments to escape usage of -rpath so it is seen by linker, but not by libtool,
enabling libexchange.la to install below /usr/lib/evolution-data-server-1.2/camel-providers, rather
than /usr/lib/evolution/2.2

* Mon Jan 31 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.4-2
- Split out the 64-bit acinclude.m4 patch into two patches, one containing the "actual" patch; the other containing all of the regenerated autotool results.
- Actually apply the 64-bit acinclude.m4 fix this time.

* Wed Jan 26 2005 David Malcolm <dmalcolm@redhat.com> - 2.1.4-1
- Update from stable upstream 2.0.3 to unstable upstream 2.1.4
- Update evo_major from 2.0 to 2.2
- Added eds_major definition
- Require evolution 2.1.4
- Require libsoup 2.2.2
- Re-enable s390 architectures
- Cope with camel-providers now being stored below evolution-data-server, rather than evolution.
- Remove .a files from camel-providers subdir
- Removed various docs no longer present

* Wed Dec 15 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.3-1
- Update from upstream 2.0.2 to 2.0.3
- The fix for bugs #139134 and #141419 is now in the upstream tarball; removing the patch

* Tue Nov 30 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.2-2
- Added domain-fix.patch to fix bugs #139134 and #141419

* Tue Oct 12 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.2-1
- Update from 2.0.1 to 2.0.2
- exclude s390/s390x architecture for now due to Mozilla build problems
- refresh the autogenerated parts of the 64bit fix patch to patch over the latest version of autogenerated files from upstream

* Fri Oct  1 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.1-5
- added explicit gnutls requirement

* Fri Oct  1 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.1-4
- set libsoup requirement to be 2.2.0-2, to ensure gnutls support has been added

* Fri Oct  1 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.1-3
- added requirement on libsoup

* Fri Oct  1 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.1-2
- rebuild

* Thu Sep 30 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.1-1
- update from 2.0.0 to 2.0.1
- update required version of evolution from 1.5.94.1 to 2.0.1
- refresh the autogenerated parts of the 64bit fix patch to patch over the latest version of autogenerated files from upstream

* Mon Sep 20 2004 David Malcolm <dmalcolm@redhat.com>
- rebuilt

* Tue Sep 14 2004 David Malcolm <dmalcolm@redhat.com> - 2.0.0-1
- update from 1.5.94.1 to 2.0.0
- update source FTP location from 1.5 to 2.0

* Wed Sep  1 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.94.1-1
- update tarball and evolution-version from 1.5.93 to 1.5.94.1
- convert various occurrences of "1.5" in paths to "2.0" to reflect reorganisations of evolution and the connector
- refresh the autogenerated parts of the 64bit fix patch to patch over the latest version of autogenerated files from upstream

* Wed Aug 25 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.93-1
- updated from 1.5.92 to 1.5.93
- removed patch to compile against Evolution 1.5.93 (no longer needed; also was causing bug #130840)
- removed patch for LDAP detection
- added a patch to acinclude.m4 and configure.in to detect and use correct library paths (together with patching the files generated by autotools)

* Mon Aug 23 2004 Nalin Dahyabhai <nalin@redhat.com> - 1.5.92-3
- change macro names to not use "-"
- fix configure on multilib systems

* Fri Aug 20 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.92-2
- exclude ppc64 architecture due to Mozilla build problems

* Thu Aug 19 2004 Nalin Dahyabhai <nalin@redhat.com> 1.5.92-1
- Require a version of openldap-devel which provides evolution-specific libs.
- Use the evolution-specific static libraries from openldap-devel, taking into
  account the value of gcc's multidir setting.
- Set $LIBS before running configure so that libldap's dependencies get pulled
  in and we don't accidentally link against the system-wide copy, which would
  make all of this hoop jumping pointless.
- Tag translation files as language-specific using %%{find_lang}.
- Update to 1.5.92.
- Patch to compile against Evolution 1.5.93.

* Mon Jul 26 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.91-1
- Updated to version 1.5.91; updated evolution version to 1.5.91

* Tue Jul  6 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.90-1
- Updated to version 1.5.90; updated evolution version to 1.5.90

* Mon Jun 21 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.9-2
- actually uploaded the source tarball this time

* Mon Jun 21 2004 David Malcolm <dmalcolm@redhat.com> - 1.5.9-1
- 1.5.9 - first version for the 1.5.* series of Evolution: use revised LDAP detection, fix a build problem in migr-test, use -rpath with evolution 1.5's privlibdir

* Thu May 13 2004 David Malcolm <dmalcolm@redhat.com> - 1.4.7-1
- downgrade to version 1.4.7 for now; add various open-ldap requirements and configuration options

* Thu May 13 2004 David Malcolm <dmalcolm@redhat.com> - 1.4.7.1-1
- updated version to 1.4.7.1

* Wed May 12 2004 David Malcolm <dmalcolm@redhat.com> - 1.4.7-1
- added ldconfig foo; build requires evolution-devel

* Tue May 11 2004 Tom "spot" Callaway <tcallawa@redhat.com>
- initial package
